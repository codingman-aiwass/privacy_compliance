package android;
import soot.jimple.infoflow.android.axml.AXmlAttribute;
import soot.jimple.infoflow.android.axml.AXmlNode;
import soot.jimple.infoflow.android.manifest.ProcessManifest;
import soot.jimple.infoflow.android.manifest.binary.BinaryManifestActivity;
import soot.jimple.infoflow.android.manifest.binary.BinaryManifestBroadcastReceiver;
import soot.jimple.infoflow.android.manifest.binary.BinaryManifestContentProvider;
import soot.jimple.infoflow.android.manifest.binary.BinaryManifestService;

import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class ComponentManager {
	private static ComponentManager singleton;

	private Map<String, ComponentBean> compMap;

	enum COMPONENT_TYPE {
		ACTIVITY, SERVICE, RECEIVER, PROVIDER;
	}

	private ComponentManager() {
		this.compMap = new HashMap<>();
	}

	public static ComponentManager getInstance() {
		if (singleton == null) {
			singleton = new ComponentManager();
		}
		return singleton;
	}

	public ComponentBean getComponent(String name) {
		return this.compMap.get(name);
	}

	public boolean hasComponent(String name) {
		return this.compMap.containsKey(name);
	}

	public Set<String> getComponentNames() {
		return compMap.keySet();
	}

	private void parseComponent(AXmlNode nd, ComponentBean comp,String pkgName) {
		Map<String, AXmlAttribute<?>> attributes = nd.getAttributes();
		for (String k : attributes.keySet()) {
			if ("name".equals(k)) {
				String componentName = (String) ((AXmlAttribute<?>) attributes.get(k)).getValue();
				if (componentName.startsWith(".")) {
					componentName = String.valueOf(pkgName) + componentName;
				} else if (!componentName.contains(".")) {
					componentName = String.valueOf(pkgName) + "." + componentName;
				}
				comp.setName(componentName);
			}
			if ("exported".equals(k)) {
				comp.setExported(((Boolean) ((AXmlAttribute<?>) attributes.get(k)).getValue()).booleanValue());
			}

			if ("permission".equals(k)) {
				comp.setPermission((String) ((AXmlAttribute<?>) attributes.get(k)).getValue());
			}
		}
		List<AXmlNode> children = nd.getChildren();
		for (AXmlNode node : children) {
			if ("intent-filter".equals(node.getTag())) {
				for (AXmlNode child : node.getChildren()) {
					if ("action".equals(child.getTag())) {
						for (String actionName : child.getAttributes().keySet()) {
							if ("name".equals(actionName)) {
								comp.setAction(
										(String) ((AXmlAttribute<?>) child.getAttributes().get(actionName)).getValue());
							}
						}
					}
				}
			}
		}
	}

	public void parseApkForComponents(String apkPath) {
		String fileName = apkPath.substring(apkPath.lastIndexOf('/') + 1, apkPath.lastIndexOf(".apk"));
		try {
			ProcessManifest processManifest = new ProcessManifest(apkPath);
            String apkPackageName = processManifest.getPackageName();
			for (BinaryManifestActivity nd : processManifest.getActivities()) {
				ComponentBean comp = new ComponentBean(fileName, apkPackageName, COMPONENT_TYPE.ACTIVITY);
				parseComponent(nd.getAXmlNode(), comp,apkPackageName);
				if (comp.getName() != null) {
					this.compMap.put(comp.getName(), comp);
				}
			}
			for (BinaryManifestService nd : processManifest.getServices()) {
				ComponentBean comp = new ComponentBean(fileName, apkPackageName, COMPONENT_TYPE.SERVICE);
				parseComponent(nd.getAXmlNode(), comp,apkPackageName);
				if (comp.getName() != null) {
					this.compMap.put(comp.getName(), comp);
				}
			}
			for (BinaryManifestBroadcastReceiver nd : processManifest.getBroadcastReceivers()) {
				ComponentBean comp = new ComponentBean(fileName, apkPackageName, COMPONENT_TYPE.RECEIVER);
				parseComponent(nd.getAXmlNode(), comp,apkPackageName);
				if (comp.getName() != null) {
					this.compMap.put(comp.getName(), comp);
				}
			}
			for (BinaryManifestContentProvider nd : processManifest.getContentProviders()) {
				ComponentBean comp = new ComponentBean(fileName, apkPackageName, COMPONENT_TYPE.PROVIDER);
				parseComponent(nd.getAXmlNode(), comp,apkPackageName);
				if (comp.getName() != null) {
					this.compMap.put(comp.getName(), comp);
				}
			}
			processManifest.close();
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	public boolean isAppDeveloperClass(String clazzName) {
		/*
		 * return true if the package name has ever appeared in manifest
		 */
		for (String item : compMap.keySet()) {
			if (commonDotsInPrefix(clazzName, item) >= 2) {
				return true;
			}
		}

		/*
		 * return true if the package name is obfuscated
		 */
		Pattern r = Pattern.compile("^[a-zA-Z]{1}\\.[a-zA-Z]{1}\\.");
		Matcher m = r.matcher(clazzName);
		if (m.find()) {
			return true;
		}

		return false;
	}

	public class ComponentBean {
		private String app;

		private String pkg;

		private COMPONENT_TYPE type;

		private String name;

		private Boolean exported;

		private String permission;

		private Set<String> actions;

		public ComponentBean(String app, String pkg, COMPONENT_TYPE type) {
			this.app = app;
			this.pkg = pkg;
			this.type = type;
			this.exported = null;
			this.actions = new HashSet<>();
		}

		public String getApp() {
			return this.app;
		}

		public void setApp(String app) {
			this.app = app;
		}

		public String getPkg() {
			return this.pkg;
		}

		public void setPkg(String pkg) {
			this.pkg = pkg;
		}

		public COMPONENT_TYPE getType() {
			return this.type;
		}

		public void setType(COMPONENT_TYPE type) {
			this.type = type;
		}

		public String getName() {
			return this.name;
		}

		public void setName(String name) {
			this.name = name;
		}

		public boolean isExported() {
			return this.exported.booleanValue();
		}

		public void setExported(boolean exported) {
			this.exported = Boolean.valueOf(exported);
		}

		public String getPermission() {
			return this.permission;
		}

		public void setPermission(String permission) {
			this.permission = permission;
		}

		public Set<String> getActions() {
			return this.actions;
		}

		public void setAction(String action) {
			this.actions.add(action);
		}
	}
    public static int commonDotsInPrefix(String phrase1, String phrase2) {
		int dotCnt = 0;
		int minLength = Math.min(phrase1.length(), phrase2.length());
		for (int i = 0; i < minLength; i++) {
			if (phrase1.charAt(i) != phrase2.charAt(i)) {
				break;
			}

			if (phrase1.charAt(i) == '.') {
				dotCnt += 1;
			}
		}

		return dotCnt;
	}
}