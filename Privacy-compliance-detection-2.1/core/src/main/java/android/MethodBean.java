package android;

import soot.jimple.Stmt;

import java.util.HashSet;

public class MethodBean {
    public String clazz;
    public HashSet<String> privacy_data_items;
    public HashSet<Stmt> third_party_stmt;
    public HashSet<String> data_items;
    public HashSet<Stmt> stmt_contain_privacy_item;
    public HashSet<Stmt> stmt_only_contain_string_constant;

    public HashSet<String> stmt_method_contain_privacy_item;
    public HashSet<String> third_party_stmt_method_contain_privacy_item;
    public HashSet<String> stmt_method_only_contain_string_constant;
    public HashSet<String> third_party_privacy_data_items;

    public MethodBean(String clazz) {
        this.clazz = clazz;
        this.privacy_data_items = new HashSet<>();
        this.data_items = new HashSet<>();
        this.stmt_contain_privacy_item = new HashSet<>();
        this.stmt_only_contain_string_constant = new HashSet<>();
        this.third_party_stmt = new HashSet<>();

        this.stmt_method_contain_privacy_item = new HashSet<>();
        this.third_party_stmt_method_contain_privacy_item = new HashSet<>();
        this.stmt_method_only_contain_string_constant = new HashSet<>();
        this.third_party_privacy_data_items = new HashSet<>();
    }

    @Override
    public String toString() {
        return "MethodBean{" +
                "clazz='" + clazz + '\'' +
                ", privacy_data_items=" + privacy_data_items +
                ", num of privacy_data_items=" + privacy_data_items.size() +
                ", stmt_method_contain_privacy_item=" + stmt_method_contain_privacy_item +
                ", stmt_method_only_contain_string_constant=" + stmt_method_only_contain_string_constant +
                ", third_party_privacy_data_items=" + third_party_privacy_data_items + 
                ", num of third_party_privacy_data_items=" + third_party_privacy_data_items.size() + 
                '}';
    }
}
