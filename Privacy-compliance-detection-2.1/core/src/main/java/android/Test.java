package android;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileFilter;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Arrays;
public class Test {
    public static double levenshteinDistance(String s1, String s2) {
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
        
        return (1 - ((double) dp[m][n] / Math.max(m,n)));
    }
    public static void test01(){
        String apkResult_2 = "./result_0509" + File.separator + "/home/chenzhefan/project/myIoTProfiler02/test_apk/".replaceAll(".*/", "").replaceAll(".apk", "")
                + "_method_scope.json";
        System.out.println(apkResult_2);
    }
    public static void test02(){
        ArrayList<String> apksToAnalysis = new ArrayList<>();
        apksToAnalysis.add("/home/chenzhefan/project/myIoTProfiler02/test_apk");
        apksToAnalysis.add("/home/chenzhefan/project/myIoTProfiler02/test_apk");
        // for(String apk:apksToAnalysis){
        //     System.out.println(apk);
        // }
        File file1 = new File("/home/chenzhefan/project/myIoTProfiler02/test_apk");
        System.out.println(file1.getAbsolutePath());
        File file2 = new File("/home/chenzhefan/project/myIoTProfiler02/test_apk/test.apk");
        System.out.println(file2.getAbsolutePath());
        System.out.println(file1.exists());
        System.out.println(file2.exists());
    }
    public static void test03(){
        String path1 = "/home/chenzhefan/project/myIoTProfiler02/test_apk";
        String path2 = "/home/chenzhefan/project/myIoTProfiler02/test_apks/";
        File[] apkList1 = new File(path1).listFiles(new FileFilter() {
            public boolean accept(File file) {
                return file.isFile() && file.getName().endsWith(".apk");
            }
        });
        for(File apk : apkList1){
            System.out.println(apk.getAbsolutePath());
        }
        System.out.println("======================");
        File[] apkList2 = new File(path2).listFiles(new FileFilter() {
            public boolean accept(File file) {
                return file.isFile() && file.getName().endsWith(".apk");
            }
        });
        for(File apk : apkList2){
            System.out.println(apk.getAbsolutePath());
        }
        System.out.println("======================");
    }
    public static void test04(){
        String path = "/home/czf/";
        File[] apkList = new File(path).listFiles(new FileFilter() {
            public boolean accept(File file) {
                return file.isFile() && file.getName().endsWith(".apk");
            }
        });
        if (apkList == null) {
            System.out.println("apkList is null..");
            return;
        }
        for(File file:apkList){
            System.out.println(file.getAbsolutePath());
        }
    }
    public static void main(String[] args) {
        for (String apkList : ReadApks.getApkList()) {
            // System.out.println(apkList);

            // String command = "aapt dump badging " + apkList + " |& grep -o \"package: name='\\S*'\" | sed \"s/package: name='\\(.*\\)'/'\\1'/\" | tr -d \"'\"";
            // String command = String.format("~/android/sdk/build-tools/30.0.1/aapt dump badging %s |& grep -o \"package: name='\\S*'\" | sed \"s/package: name='\\(.*\\)'/'\\1'/\" | tr -d \"'\"",apkList);
            // System.out.println("command execute:" + command);
            // System.out.println(command);
            // try {
            //     ProcessBuilder builder = new ProcessBuilder();
            //     builder.command("bash", "-c", command);
            //     builder.redirectErrorStream(true);
            //     Process process = builder.start();
            //     BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            //     BufferedReader errorReader = new BufferedReader(new InputStreamReader(process.getErrorStream())); // add a separate reader for the error stream
            //     String line;
            //     while ((line = reader.readLine()) != null) {
            //         System.out.println("output info:" + line);
            //     }
            //     while ((line = errorReader.readLine()) != null) { // print any output from the error stream
            //         System.out.println("error info:" + line);
            //     }
            //     int exitCode = process.waitFor();
            //     System.out.println("Exited with error code " + exitCode);
            // } catch (Exception e) {
            //     e.printStackTrace();
            // }
            System.out.println(GetApkPackageName.get(apkList));
        }

    }
}


