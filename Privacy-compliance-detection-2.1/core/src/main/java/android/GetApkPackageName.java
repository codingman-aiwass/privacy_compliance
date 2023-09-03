package android;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.Properties;

public class GetApkPackageName {
    public static String get(String apkPath){
        String aapt = null;
        Properties properties = new Properties();
        try {
            properties.load(new FileReader("./RunningConfig.properties"));
        } catch (IOException e) {
            e.printStackTrace();
        }
        aapt = properties.getProperty("aapt");
        String command = String.format("%s dump badging %s |& grep -o \"package: name='\\S*'\" | sed \"s/package: name='\\(.*\\)'/'\\1'/\" | tr -d \"'\"",aapt,apkPath);
        String line = null;
        try {
            ProcessBuilder builder = new ProcessBuilder();
            builder.command("bash", "-c", command);
            builder.redirectErrorStream(true);
            Process process = builder.start();
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            
            while ((line = reader.readLine()) != null) {
                return line;
            }

        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }
}
