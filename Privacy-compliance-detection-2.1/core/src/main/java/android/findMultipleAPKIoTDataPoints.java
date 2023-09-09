package android;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import org.xmlpull.v1.XmlPullParserException;
import soot.*;
import soot.jimple.InvokeExpr;
import soot.jimple.Stmt;
import soot.jimple.StringConstant;
import soot.jimple.infoflow.android.manifest.ProcessManifest;
import soot.options.Options;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Paths;
import java.text.SimpleDateFormat;
import java.util.*;
import java.util.concurrent.*;

public class findMultipleAPKIoTDataPoints {
    public static String logsPath = "";
    public static String androidJar = "";
    public static String resultSavePath = "";
    public static boolean printToFile;
    private static final List<String> excludePackagesList = new ArrayList<String>();
    public static Properties interestAPIproperties;
    public static Properties thirdPartyProperties;
    public static Set<Object> keySet;
    public static Set<Object> thirdPartyList;
    public static Set<String> privacyItemList;
    public static int privacy_item_num_threshold = 2;
    public static SimpleDateFormat dateFormat = new SimpleDateFormat("YYYY-MM-dd_HH-mm-ss");
    // 从配置文件中读取的apkPath 可以是若干个apk文件的绝对路径,也可以是若干个包含许多apk文件的文件夹的绝对路径
    public static String apkPath = "";

    public static String aapt = "";

    static {
        dateFormat.setTimeZone(TimeZone.getTimeZone("Asia/Shanghai"));
        // 读取properties文件
        interestAPIproperties = new Properties();
        try {
            interestAPIproperties.load(new FileReader("config" + File.separator + "interestedAPIs.properties"));
        } catch (IOException e) {
            e.printStackTrace();
        }
        keySet = interestAPIproperties.keySet();
        // 读取第三方列表
        thirdPartyProperties = new Properties();
        try {
            thirdPartyProperties.load(new FileReader("config" + File.separator + "3rd_sdks.properties"));
        } catch (IOException e) {
            e.printStackTrace();
        }
        thirdPartyList = thirdPartyProperties.keySet();
        privacyItemList = readTxt("config" + File.separator + "privacy_items.txt");
    }

    static {
        excludePackagesList.add("java.");
        excludePackagesList.add("android");
        excludePackagesList.add("androidx.");
        excludePackagesList.add("android.R");
        excludePackagesList.add("junit.");
        excludePackagesList.add("org.");
        excludePackagesList.add("org.apache");
        excludePackagesList.add("dalvik.");
        excludePackagesList.add("roboguice");

        excludePackagesList.add("javax.");
        excludePackagesList.add("android.support.");
        excludePackagesList.add("sun.");
        excludePackagesList.add("com.google.");
    }

    public static void main(String[] args) throws IOException {
        Date date2 = new Date();
        String timeNow = dateFormat.format(date2).toString();
        BufferedWriter bw = new BufferedWriter(new FileWriter("analysis_" + timeNow + ".log"));
        setUpConfig();

        ArrayList<String> apksToAnalysis = new ArrayList<>();
        ArrayList<String> apkFoldersToAnalysis = new ArrayList<>();
        // 判断输入的apk参数是否包含多个apk的绝对路径,或者包含多个文件夹的绝对路径
        String[] apks = apkPath.split(";");
        if (apks.length == 1) {
            // 说明只输入了一个绝对路径,判断这个绝对路径是apk的还是文件夹的
            if (apks[0].endsWith(".apk")) {
                // 表示输入了一个apk的绝对路径
                apksToAnalysis.add(apks[0]);
            } else {
                // 表示输入了一个文件夹的绝对路径
                apkFoldersToAnalysis.add(apks[0]);
            }
        } else if (apks.length > 1) {
            // 说明输入了多个apk或者文件夹的绝对路径
            for (String apk : apks) {
                if (apk.endsWith(".apk")) {
                    apksToAnalysis.add(apk);
                } else {
                    apkFoldersToAnalysis.add(apk);
                }
            }
        } else {
            bw.write("Input nothing,exit...");
            bw.flush();
            bw.close();
            return;
        }
        try {
            ArrayList<String> totalApks = new ArrayList<>();
            totalApks.addAll(apksToAnalysis);
            for (String apksFolder : apkFoldersToAnalysis) {
                File[] apkList = new File(apksFolder).listFiles(new FileFilter() {
                    public boolean accept(File file) {
                        return file.isFile() && file.getName().endsWith(".apk");
                    }
                });
                if (apkList == null) {
                    bw.write(apksFolder + " not exists, analyze next...");
                    bw.newLine();
                    bw.flush();
                    continue;
                }
                for (File apkFile : apkList) {
                    totalApks.add(apkFile.getAbsolutePath());
                }
            }
//             在此处保存所指定的所有apk的包名列表到动态app分析里
            BufferedWriter pkgWriter = new BufferedWriter(new OutputStreamWriter(new FileOutputStream(new File(".." + File.separator + ".." + File.separator + "AppUIAutomator2Navigation" + File.separator + "apk_pkgName.txt")), StandardCharsets.UTF_8));

            for(String apk:totalApks){
                ProcessManifest processManifest;
                String apkPackageName = null;
                String apkName = null;
                try {
                    processManifest = new ProcessManifest(apk);
                    apkPackageName = processManifest.getPackageName();
                    apkName = GetApkPackageName.getAppName(apk);
                    
                    // System.out.println(apk);
                    // System.out.println(apkPackageName);
                    pkgWriter.write(apkPackageName + " | " + apkName);
                    pkgWriter.newLine();
                    pkgWriter.flush();
                } catch (XmlPullParserException e) {
                    // TODO Auto-generated catch block
                    e.printStackTrace();
                }
            }
            pkgWriter.close();
            for (String apk : totalApks) {
                try {
                    System.setOut(System.out);
                    System.out.println("analyze " + apk + "===================");
                    Date date = new Date();
                    if (new File(apk).exists()) {
                        bw.write("analyze " + apk + " at " + dateFormat.format(date).toString());
                        bw.newLine();
                        bw.flush();
                        runSingleAnalysisWithTimeout(apk, printToFile, resultSavePath, 3600);
                    } else {
                        bw.write(apk + " not exists,analyze next...");
                        bw.newLine();
                        bw.flush();
                        continue;
                    }

                } catch (IOException e) {
                    System.out.println("locallized error info in multiRun singleAnalysis:" + e.getLocalizedMessage());
                    System.out.println("error info:" + e.getMessage());
                    System.out.println(Arrays.toString(e.getStackTrace()));
                }
            }
        } catch (Exception e) {
            bw.write("Error occurred in outter try.. Error Info:" + e.getMessage());
            bw.newLine();
            bw.write("Localized Error Info:" + e.getLocalizedMessage());
            bw.newLine();
            bw.write(Arrays.toString(e.getStackTrace()));
            bw.newLine();
        }
        bw.close();
        System.exit(0);
    }

    public static Set<String> readTxt(String filePath) {
        HashSet<String> set = new HashSet<>();

        try (BufferedReader br = new BufferedReader(new FileReader(filePath))) {
            String line;
            while ((line = br.readLine()) != null) {
                set.add(line);
            }
        } catch (IOException e) {
            System.err.format("IOException: %s%n", e);
        }
        return set;
    }

    public static void runSingleAnalysisWithTimeout(String appPath, boolean printToFile, String resultSavePath,
            long timeoutInSeconds) {
        ExecutorService executor = Executors.newSingleThreadExecutor();
        Future<?> future = executor.submit(() -> {
            try {
                singleAnalysis(appPath, printToFile, resultSavePath);
            } catch (IOException e) {
                e.printStackTrace();
            }
        });
        try {
            future.get(timeoutInSeconds, TimeUnit.SECONDS);
        } catch (TimeoutException e) {
            System.out.println("Execution timed out after " + timeoutInSeconds + " seconds.");
            future.cancel(true); // Interrupt the running thread.
        } catch (Exception e) {
            System.out.println("Error occurred during execution: " + e.getMessage());
        } finally {
            executor.shutdownNow(); // Terminate the executor service.
        }
    }

    public static void setUpConfig() throws IOException {
        Properties properties = new Properties();

        try (FileInputStream fileInputStream = new FileInputStream("RunningConfig.properties")) {
            properties.load(fileInputStream);
            printToFile = Boolean.parseBoolean(properties.getProperty("printToFile", "true"));
            logsPath = Paths.get(properties.getProperty("logsPath", "")).toString();
            androidJar = Paths.get(properties.getProperty("AndroidJar", "")).toString();
            resultSavePath = Paths.get(properties.getProperty("resultSavePath", "")).toString();
            apkPath = Paths.get(properties.getProperty("apk", "")).toString();
            aapt = Paths.get(properties.getProperty("aapt", "")).toString();

        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static void initSootConfig(String apkPath) {
        G.reset();
        Options.v().set_prepend_classpath(true);
        Options.v().set_allow_phantom_refs(true);
        Options.v().set_src_prec(Options.src_prec_apk);
        Options.v().set_output_format(Options.output_format_jimple);
        String androidJarPath = Scene.v().getAndroidJarPath(androidJar, apkPath);

        List<String> pathList = new ArrayList<String>();
        pathList.add(apkPath);
        pathList.add(androidJarPath);

        Options.v().set_process_dir(pathList);
        Options.v().set_whole_program(true);
        Options.v().set_force_android_jar(androidJarPath);
        Options.v().set_keep_line_number(true);
        Options.v().set_process_multiple_dex(true);

        Options.v().set_wrong_staticness(Options.wrong_staticness_ignore);
        Options.v().set_exclude(excludePackagesList);

        Scene.v().loadNecessaryClasses();
        PackManager.v().runPacks();
    }

    private static boolean isExcludeClass(SootClass sootClass) {
        if (sootClass.isPhantom()) {
            return true;
        }

        String packageName = sootClass.getPackageName();
        for (String exclude : excludePackagesList) {
            if (packageName.startsWith(exclude)) {
                return true;
            }
        }

        return false;
    }

    public static void checker(File apkResult, String apkResult_2) throws IOException {
        HashMap<Stmt, StmtBean> stmt2StringConstant = new HashMap<>();
        HashMap<SootMethod, MethodBean> method2StringConstant = new HashMap<>();
        long start = System.currentTimeMillis();

        // 遍历应用中的每一个类
        int third_party_privacy_data_items_cnt = 0;
        int first_party_privacy_data_items_cnt = 0;
        int third_party_sdk_cnt = 0;
        for (SootClass sootClass : Scene.v().getApplicationClasses()) {
            if (isExcludeClass(sootClass)) {
                continue;
            }
            List<SootMethod> methods = null;
            boolean isException = false;
            // 遍历类中的每一个方法
            try {
                // System.out.println("开始遍历" + sootClass.getName() + "中的方法...");
                methods = sootClass.getMethods();
            } catch (Exception e) {
                System.out.println("try exception:");
                System.out.println("error info:" + e.getMessage());
                System.out.println("sootClass:" + sootClass.getName());
                System.out.println("Stacktrace:" + Arrays.toString(e.getStackTrace()));
                isException = true;
            }
            if (isException) {
                continue;
            }
            try {
                for (SootMethod sootMethod : methods) {
                    if (!sootMethod.hasActiveBody()) {
                        continue;
                    }
                    int index = 0;// 为了记录当前stmt是方法体中的第几个
                    String packageName = sootMethod.getDeclaringClass().getPackageName();
                    String methodSubSignature = sootMethod.getSubSignature();
                    String className = sootMethod.getDeclaringClass().getName();
                    ClassNameMethodNamePair classNameMethodNamePair = new ClassNameMethodNamePair(className,
                            methodSubSignature);
                    // 遍历方法中所有的stmt
                    MethodBean methodBean = new MethodBean(className);
                    UnitPatchingChain units = sootMethod.getActiveBody().getUnits();
                    for (Unit unit : units) {
                        boolean is3rdParty = false;
                        ++index;
                        for (Object o : thirdPartyList) {
                            String thirdPartyLibraryName = (String) o;
                            if (packageName.startsWith(thirdPartyLibraryName)) {
                                is3rdParty = true;
                                ++third_party_sdk_cnt;
                                break;
                            }
                        }
                        Stmt stmt = (Stmt) unit;
                        HashSet<String> stmtHashset = new HashSet<>();
                        List<ValueBox> useBoxes = stmt.getUseBoxes();
                        for (ValueBox useBox : useBoxes) {
                            Value value = useBox.getValue();
                            if (value instanceof StringConstant) {
                                // 添加一些判断条件,以去掉一些明显不可能是Privacy Data Point的String constant
                                String tmp = value.toString();
                                if (tmp.contains("()") || tmp.contains(".") || tmp.length() > 30 ||
                                        tmp.length() < 4 || tmp.contains("!")) {
                                    continue;
                                }
                                SootMethod method = null;
                                SootClass declaringClass = null;
                                boolean flag = false;
                                try {
                                    method = stmt.getInvokeExpr().getMethod();
                                    declaringClass = method.getDeclaringClass();
                                } catch (Exception e) {
                                    flag = true;
                                }
                                if (flag) {
                                    continue;
                                }
                                if (!keySet.contains(declaringClass.getName())) {
                                    continue;
                                }
                                String content = (String) interestAPIproperties.get(declaringClass.getName());
                                // 可以在这里加上词性还原
                                boolean NLPError = false;
                                try {
                                    tmp = ProcessStr.preProcessingSingle(tmp);
                                } catch (Exception e) {
                                    System.out.println("An error occurred in word reduction...");
                                    System.out.println("word producing:" + tmp);
                                    NLPError = true;
                                }
                                if (NLPError) {
                                    continue;
                                }
                                // 判断这个字符串是否在字符串字典里
                                boolean isPrivacyItem = false;
                                for (String s : privacyItemList) {
                                    // if (tmp.contains(s)) {
                                    // 判断策略为 编辑距离相似度 > 0.75 || 以隐私数据项开头 || 以隐私数据项结尾
                                    if (getEditDistanceSimilarity(tmp, s) > 0.75 || tmp.startsWith(s)
                                            || tmp.endsWith(s)) {
                                        isPrivacyItem = true;
                                        break;
                                    }
                                }
                                boolean isAddToStmtHashset = false;
                                if (content.equals("0")) {
                                    stmtHashset.add(tmp);
                                    // methodBean.stmt_only_contain_string_constant.add(stmt);
                                    methodBean.stmt_method_only_contain_string_constant
                                            .add(method.getSubSignature());
                                    methodBean.data_items.add(tmp);
                                    isAddToStmtHashset = true;
                                } else if (!content.contains(";")) {
                                    if (method.getSubSignature().contains(content)) {
                                        stmtHashset.add(tmp);
                                        // methodBean.stmt_only_contain_string_constant.add(stmt);
                                        methodBean.stmt_method_only_contain_string_constant
                                                .add(method.getSubSignature());
                                        methodBean.data_items.add(tmp);
                                        isAddToStmtHashset = true;
                                    }
                                } else if (content.contains(";")) {
                                    String[] specifiedMethods = content.split(";");
                                    for (String specifiedMethod : specifiedMethods) {
                                        if (method.getSubSignature().contains(specifiedMethod)) {
                                            stmtHashset.add(tmp);
                                            // methodBean.stmt_only_contain_string_constant.add(stmt);
                                            methodBean.stmt_method_only_contain_string_constant
                                                    .add(method.getSubSignature());
                                            methodBean.data_items.add(tmp);
                                            isAddToStmtHashset = true;
                                        }
                                    }
                                }
                                // 再判断,方法的返回值有没有JSON对象,有的话,也加进来
                                else {
                                    Type returnType = method.getReturnType();
                                    if (returnType instanceof RefType && ((RefType) returnType).getClassName()
                                            .equals("org.json.JSONObject")) {
                                        stmtHashset.add(tmp);
                                        // methodBean.stmt_only_contain_string_constant.add(stmt);
                                        methodBean.stmt_method_only_contain_string_constant
                                                .add(method.getSubSignature());
                                        methodBean.data_items.add(tmp);
                                        isAddToStmtHashset = true;
                                    }
                                }
                                // 如果该数据项是隐私数据点且在我们限定的几类stmt中
                                if (isPrivacyItem && isAddToStmtHashset) {
                                    if (is3rdParty) {
                                        methodBean.third_party_privacy_data_items.add(tmp);
                                        third_party_privacy_data_items_cnt++;
                                        methodBean.third_party_stmt_method_contain_privacy_item
                                                .add(method.getSubSignature());
                                    } else {
                                        methodBean.privacy_data_items.add(tmp);
                                        first_party_privacy_data_items_cnt++;
                                        methodBean.stmt_method_contain_privacy_item.add(method.getSubSignature());
                                    }
                                }
                            }
                        }
                        int hash = -1;
                        if (stmt.containsInvokeExpr()) {
                            hash = getInvokeExprHash(stmt.getInvokeExpr());
                        }
                        if (!stmtHashset.isEmpty()) {
                            if (is3rdParty) {
                                stmt2StringConstant.put(stmt,
                                        new StmtBean(stmtHashset, true, classNameMethodNamePair, index, hash));
                            } else {
                                stmt2StringConstant.put(stmt,
                                        new StmtBean(stmtHashset, false, classNameMethodNamePair, index, hash));
                            }
                        }

                    }
                    if (methodBean.privacy_data_items.size() +
                            methodBean.third_party_privacy_data_items.size() >= privacy_item_num_threshold) {
                        method2StringConstant.put(sootMethod, methodBean);
                    }
                }
            } catch (Exception e) {
                System.out.println("error in line 160");
                System.out.println("sootClass:" + sootClass.getName());
                System.out.println("method list:" + methods);
                System.out.println("Error info:" + e.getMessage());
                System.out.println("error info localized:" + e.getLocalizedMessage());
                System.out.println("stacktrace" + Arrays.toString(e.getStackTrace()));
            }

        }

        // BufferedWriter bufferedWriter = new BufferedWriter(new FileWriter(apkResult));
        // Iterator<Map.Entry<Stmt, StmtBean>> iterator = stmt2StringConstant.entrySet().iterator();
        // while (iterator.hasNext()) {
        //     Map.Entry<Stmt, StmtBean> next = iterator.next();
        //     Stmt key = next.getKey();
        //     StmtBean value1 = next.getValue();
        //     // StringConstant_isThirdParty values = next.getValue();
        //     // HashSet<String> values = next.getValue();
        //     StringBuilder value_sb = new StringBuilder();
        //     for (String s : value1.hashSet) {
        //         value_sb.append(s).append("######");
        //     }
        //     String value = value_sb.toString();
        //     bufferedWriter.write(key + "|||" + value + "|||" + value1.isThirdParty +
        //             "|||" + value1.classNameMethodNamePair + "|||" + value1.index + "|||" +
        //             value1.hash);
        //     bufferedWriter.newLine();
        // }
        System.out.println("Collect " + method2StringConstant.size() + " method(s)");
        System.out.println("Collect " + third_party_sdk_cnt + " 3rd stmt(s)");
        System.out.println("Collect " + first_party_privacy_data_items_cnt + " 1st privacy data item(s)..");
        System.out.println("Collect " + third_party_privacy_data_items_cnt + " 3rd privacy data item(s)..");
        if (method2StringConstant.size() == 0) {
            System.out.println("Nothing to output to json file,exit...");
            return;
        }

        JsonArray method_arr = new JsonArray();
        for (SootMethod method : method2StringConstant.keySet()) {
            MethodBean methodBean = method2StringConstant.get(method);
            JsonObject method_json = new JsonObject();
            method_json.addProperty("clazz", methodBean.clazz);
            method_json.addProperty("method", method.toString());
            method_json.addProperty("privacy_data_items", String.valueOf(methodBean.privacy_data_items));
            method_json.addProperty("num_of_privacy_data_items", methodBean.privacy_data_items.size());
            method_json.addProperty("data_items", String.valueOf(methodBean.data_items));
            method_json.addProperty("num_of_data_items", methodBean.data_items.size());
            // method_json.addProperty("stmt_contain_privacy_item",
            // String.valueOf(methodBean.stmt_contain_privacy_item));
            // method_json.addProperty("num_of_stmt_contain_privacy_item",
            // methodBean.stmt_contain_privacy_item.size());
            // method_json.addProperty("stmt_only_contain_string_constant",
            // String.valueOf(methodBean.stmt_only_contain_string_constant));
            // method_json.addProperty("num_of_stmt_only_contain_string_constant",
            // methodBean.stmt_only_contain_string_constant.size());
            // method_json.addProperty("3rd_stmt",
            // String.valueOf(methodBean.third_party_stmt));
            // method_json.addProperty("num_of_3rd_stmt",
            // methodBean.third_party_stmt.size());
            method_json.addProperty("stmt_method_contain_privacy_item",
                    String.valueOf(methodBean.stmt_method_contain_privacy_item));
            method_json.addProperty("num_of_stmt_method_contain_privacy_item",
                    methodBean.stmt_method_contain_privacy_item.size());
            method_json.addProperty("stmt_method_only_contain_string_constant",
                    String.valueOf(methodBean.stmt_method_only_contain_string_constant));
            method_json.addProperty("num_stmt_method_only_contain_string_constant",
                    methodBean.stmt_method_only_contain_string_constant.size());
            method_json.addProperty("3rd_stmt_method_contain_privacy_item",
                    String.valueOf(methodBean.third_party_stmt_method_contain_privacy_item));
            method_json.addProperty("num_of_3rd_stmt_method_contain_privacy_item",
                    methodBean.third_party_stmt_method_contain_privacy_item.size());
            method_json.addProperty("3rd_privacy_data_items",
                    String.valueOf(methodBean.third_party_privacy_data_items));
            method_json.addProperty("num_3rd_privacy_data_item", methodBean.third_party_privacy_data_items.size());
            method_arr.add(method_json);
        }

        try (FileWriter file = new FileWriter(apkResult_2)) {
            Gson gson = new GsonBuilder().setPrettyPrinting().create();
            gson.toJson(method_arr, file);
        } catch (IOException e) {
            System.err.format("IOException: %s%n", e);
        }
        // System.out.printf("一共收集了%d个stmt\n", stmt2StringConstant.size());
        // bufferedWriter.close();

        long end = System.currentTimeMillis();
        long cost_time = end - start;
        System.out.println("Time cost:" + cost_time);

    }

    public static void singleAnalysis(String apk, boolean printToFile, String resultSavePath) throws IOException {
        // 在此处计算得到apk的包名
        File apkFile = new File(apk);
        // String apkPackageName = GetApkPackageName.get(apk);
        ProcessManifest processManifest;
        String apkPackageName = null;
        try {
            processManifest = new ProcessManifest(apkFile);
            apkPackageName = processManifest.getPackageName();
        } catch (XmlPullParserException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }

        // File apkResult = new File(
        //         resultSavePath + File.separator + apk.replaceAll(".*/", "").replaceAll(".apk", "") + ".txt");
        // String apkResult_2 = resultSavePath + File.separator + apk.replaceAll(".*/", "").replaceAll(".apk", "")
        //         + "_method_scope.json";
        // 并将保存的文件名里的apk名换成apkPackageName
        File apkResult = new File(resultSavePath + File.separator + apkPackageName + ".txt");
        String apkResult_2 = resultSavePath + File.separator + apkPackageName + "_method_scope.json";
        if (printToFile) {
            // File outPutInfo = new File(
            //         logsPath + File.separator + apk.replaceAll(".*/", "").replaceAll(".apk", "") + "_output_info.log");
            File outPutInfo = new File(logsPath + File.separator + apkPackageName + "_output_info.log");
            if (!outPutInfo.exists()) {
                outPutInfo.createNewFile();
            } else {
                // System.out.println(logsPath + File.separator + apk.replaceAll(".*/", "").replaceAll(".apk", "")
                //         + "_output_info.log has existed,exit...");
                System.out.println(logsPath + File.separator + apkPackageName + "_output_info.log has existed,exit...");
                return;
            }
            PrintStream outStream = new PrintStream(new FileOutputStream(outPutInfo));
            System.setOut(outStream);
            if (apkResult.exists()) {
                System.out.println(apkResult + "has exited,exit...");
                return;
            }
            if (new File(apkResult_2).exists()) {
                System.out.println(apkResult_2 + "has exited,exit...");
                return;
            }
            Date date = new Date();
            System.out.println("Start analysis " + apk + " at " + dateFormat.format(date).toString());
            System.out.println("start initSootConfig()");
            try {
                initSootConfig(apk);
            } catch (Exception e) {
                System.out.println("Error in initSootConfig...");
                System.out.println("initSootConfig error info:" + e.getMessage());
                // System.out.println("StackTrace:" + Arrays.toString(e.getStackTrace()));
                System.out.println("Exit singleAnalysis due to initSootConfigError...");
                outStream.close();
                System.setOut(System.out);
                return;
            }
            System.out.println("End initSootConfig()");
            
            checker(apkResult, apkResult_2);

            outStream.close();
            System.setOut(System.out);
        } else {
            if (apkResult.exists()) {
                System.out.println(apkResult + "has exited,exit...");
                return;
            }
            initSootConfig(apk);
            checker(apkResult, apkResult_2);
        }

    }

    private static int getInvokeExprHash(InvokeExpr invokeExpr) {
        int hash = invokeExpr.getMethod().getSubSignature().hashCode();
        for (Value arg : invokeExpr.getArgs()) {
            if (arg instanceof StringConstant) {
                hash = 31 * hash + arg.hashCode();
            }
        }
        return hash;
    }

    private static double getEditDistanceSimilarity(String s1, String s2) {
        int m = s1.length();
        int n = s2.length();
        int[][] dp = new int[m + 1][n + 1];

        for (int i = 0; i <= m; i++) {
            dp[i][0] = i;
        }

        for (int j = 0; j <= n; j++) {
            dp[0][j] = j;
        }

        for (int i = 1; i <= m; i++) {
            for (int j = 1; j <= n; j++) {
                if (s1.charAt(i - 1) == s2.charAt(j - 1)) {
                    dp[i][j] = dp[i - 1][j - 1];
                } else {
                    dp[i][j] = 1 + Math.min(dp[i - 1][j - 1], Math.min(dp[i][j - 1], dp[i - 1][j]));
                }
            }
        }

        return (1 - ((double) dp[m][n] / Math.max(m, n)));
    }
}
