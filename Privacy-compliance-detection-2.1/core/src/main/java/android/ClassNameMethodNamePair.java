package android;

import java.util.Objects;

public class ClassNameMethodNamePair {
    public String className;
    public String methodName;

    public ClassNameMethodNamePair(String className, String methodName) {
        this.className = className;
        this.methodName = methodName;
    }

    @Override
    public String toString() {
        return className + "@#@#@#" + methodName;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        ClassNameMethodNamePair that = (ClassNameMethodNamePair) o;
        return className.equals(that.className) && methodName.equals(that.methodName);
    }

    @Override
    public int hashCode() {
        return Objects.hash(className, methodName);
    }
}
