package android;

import java.util.HashSet;

public class StmtBean {
    public HashSet<String> hashSet;
    public String isThirdParty;
    public ClassNameMethodNamePair classNameMethodNamePair;
    public int index;
    public int hash;


    public StmtBean(HashSet<String> hashSet,
                    Boolean isThirdParty,
                    ClassNameMethodNamePair classNameMethodNamePair,
                    int index,int hash) {
        this.hashSet = hashSet;
        if (isThirdParty) {
            this.isThirdParty = "1";
        } else {
            this.isThirdParty = "0";
        }
        this.classNameMethodNamePair = classNameMethodNamePair;
        this.index = index;
        this.hash = hash;
    }

}
