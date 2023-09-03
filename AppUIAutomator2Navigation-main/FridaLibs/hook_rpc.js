console.log("Script loaded successfully ");
Java.perform(function x() {
    var act = Java.use("android.content.Intent");
    act.getData.implementation = function() {
        var data = this.getData()
        var extra = this.getExtras()
        send(data)
        send(extra.toString())
        return data
    };

     act.getData.implementation = function() {
        var data = this.getData()
        var extra = this.getExtras()
        send(data)
        send(extra.toString())
        return data
    };

//    var Webview = Java.use("android.webkit.WebView")
//        Webview.loadUrl.overload("java.lang.String").implementation = function(url) {
//        console.log("[+]Loading URL from", url);
//        this.loadUrl.overload("java.lang.String").call(this, url);
//    }
//
//    Java.choose('android.webkit.WebView',{
//        onMatch: function (instance) {
//            console.log("Found instance: " + instance);
//            console.log("URL: "+instance.getUrl());
//        },
//        onComplete: function () {
//            console.log('Finished')
//        }
//    });

});


//console.log("Script loaded successfully ");
//
//function callSecretFun() { //定义导出函数
//    Java.perform(function () { //找到隐藏函数并且调用
//        Java.choose("android.content.Intent", {
//            onMatch: function (instance) {
//                console.log("Found intent: " + instance);
//                console.log("Data: " + instance.getData());
//                console.log("Extras: " + instance.getExtras())
//                console.log("\n")
//            },
//            onComplete: function () { }
//        });
//    });
//}
//rpc.exports = {
//    callsecretfunction: callSecretFun //把callSecretFun函数导出为callsecretfunction符号，导出名不可以有大写字母或者下划线
//};