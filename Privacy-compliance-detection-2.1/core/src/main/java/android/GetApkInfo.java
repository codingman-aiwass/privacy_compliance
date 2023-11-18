package android;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Properties;

public class GetApkInfo {
    public static void main(String[] args) throws FileNotFoundException {
        Properties properties = new Properties();
        String apkPath = null;
        try (FileInputStream fileInputStream = new FileInputStream("RunningConfig.properties")) {
            properties.load(fileInputStream);
            String[] apks = properties.getProperty("apk", "").split(";");
            StringBuilder sb = new StringBuilder();
            for (String apk : apks) {
                sb.append(Paths.get(apk));
                sb.append(";");
            }
//            apkPath = Paths.get(properties.getProperty("apk", "")).toString();
            apkPath = sb.toString().substring(0, sb.toString().length() - 1);
            System.out.println(apkPath);
        } catch (IOException e) {
            e.printStackTrace();
        }
        ArrayList<String> apksToAnalysis = new ArrayList<>();
        ArrayList<String> apkFoldersToAnalysis = new ArrayList<>();
        // 判断输入的apk参数是否包含多个apk的绝对路径,或者包含多个文件夹的绝对路径
        assert apkPath != null;
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
            System.out.println("Input nothing,exit.");
            return;
        }
        try {
            ArrayList<String> totalApks = new ArrayList<>();
            totalApks.addAll(apksToAnalysis);
            for (String apksFolder : apkFoldersToAnalysis) {
                File[] apkList = new File(apksFolder).listFiles(file -> file.isFile() && file.getName().endsWith(".apk"));
                if (apkList == null) {
                    System.out.println(apksFolder + " not exists, analyze next...");
                    continue;
                }
                for (File apkFile : apkList) {
                    totalApks.add(apkFile.getAbsolutePath());
                }
            }
//             在此处保存所指定的所有apk的包名列表到动态app分析里
            BufferedWriter pkgWriter = new BufferedWriter(new OutputStreamWriter(new FileOutputStream(new File(".." + File.separator + ".." + File.separator + "AppUIAutomator2Navigation" + File.separator + "apk_pkgName.txt")), StandardCharsets.UTF_8));

            for (String apk : totalApks) {
                String apkPackageName = null;
                String apkName = null;
                try {
                    apkPackageName = GetApkPackageName.get(apk);
                    apkName = GetApkPackageName.getAppName(apk);

                    System.out.println(apk);
                    System.out.println(apkPackageName);
                    System.out.println(apkName);
                    pkgWriter.write(apkPackageName + " | " + apkName);
                    pkgWriter.newLine();
                    pkgWriter.flush();
                } catch (IOException e) {
                    // TODO Auto-generated catch block
                    e.printStackTrace();
                }
            }
            pkgWriter.close();
        }
        catch (Exception exception){
            exception.printStackTrace();
        }


    }
}
