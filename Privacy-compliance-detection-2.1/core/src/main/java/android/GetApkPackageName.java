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
        String command = String.format("%s dump badging %s 2>&1 | grep -o \"package: name='\\S*'\" | sed \"s/package: name='\\(.*\\)'/'\\1'/\" | tr -d \"'\"",aapt,apkPath);       
        // String command = String.format("%s dump badging %s |& grep -o \"package: name='\\S*'\" | sed \"s/package: name='\\(.*\\)'/'\\1'/\" | tr -d \"'\"",aapt,apkPath);
        // System.out.println(command);
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
    public static String getAppName(String apkPath){
        String aapt = null;
        Properties properties = new Properties();
        try {
            properties.load(new FileReader("./RunningConfig.properties"));
        } catch (IOException e) {
            e.printStackTrace();
        }
        aapt = properties.getProperty("aapt");
        // String command1 = String.format("%s dump badging %s 2>&1 grep -o \"application-label-zh:'\\S*'\" | sed \"s/application-label-zh:'\\(.*\\)'/'\\1'/\" | tr -d \"'\"",aapt,apkPath);
        // String command2 = String.format("%s dump badging %s 2>&1 grep -o \"application-label-zh-CN:'\\S*'\" | sed \"s/application-label-zh-CN:'\\(.*\\)'/'\\1'/\" | tr -d \"'\"",aapt,apkPath);
        // String command3 = String.format("%s dump badging %s 2>&1 grep -o \"application-label:'\\S*'\" | sed \"s/application-label:'\\(.*\\)'/'\\1'/\" | tr -d \"'\"",aapt,apkPath);
        // String command4 = String.format("%s dump badging %s 2>&1 grep -o \"application: label='\\S*'\" | sed \"s/application: label='\\(.*\\)'/'\\1'/\" | tr -d \"'\"",aapt,apkPath);
        
        String command1 = String.format("%s dump badging %s 2>&1 | grep -o \"application-label-zh:'\\S*'\" | sed \"s/application-label-zh:'\\(.*\\)'/'\\1'/\" | tr -d \"'\"",aapt,apkPath);
        String command2 = String.format("%s dump badging %s 2>&1 | grep -o \"application-label-zh-CN'\\S*'\" | sed \"s/application-label-zh-CN'\\(.*\\)'/'\\1'/\" | tr -d \"'\"",aapt,apkPath);
        String command3 = String.format("%s dump badging %s 2>&1 | grep -o \"application-label:'\\S*'\" | sed \"s/application-label:'\\(.*\\)'/'\\1'/\" | tr -d \"'\"",aapt,apkPath);
        String command4 = String.format("%s dump badging %s 2>&1 | grep -o \"application: label='\\S*'\" | sed \"s/application: label='\\(.*\\)'/'\\1'/\" | tr -d \"'\"",aapt,apkPath);
        // System.out.println(command);| grep -o "package: name='\S*'" | sed "s/package: name='\(.*\)'/'\1'/" | tr -d "'"

        String line = null;
        for(int i = 1;i <= 4;i++){
            try {
                ProcessBuilder builder = new ProcessBuilder();
                String command = null;
                switch(i){
                    case 1:
                        command = command1;
                        break;
                    case 2:
                        command = command2;
                        break;
                    case 3:
                        command = command3;
                        break;
                    case 4:
                        command = command4;
                        break;

                }
                // System.out.println(command);
                builder.command("bash", "-c", command);
                builder.redirectErrorStream(true);
                Process process = builder.start();
                BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
                
                while ((line = reader.readLine()) != null) {
                    return line.substring(line.indexOf(":") + 1, line.length());
                }

            } catch (Exception e) {
                e.printStackTrace();
            }
            if(line != null){
                break;
            }
        }
        
        return null;
    }
}
