public class Method {
    public void first() {
        System.out.println("no parameters");
    }

    public void first(int a) {
        System.out.println(a);
    }

    public void first(int a, int b) {
        System.out.println(a + "+" + b + "=" + (a + b));
    }
}

public class Method1 {
    public static void main(String args[]) {
        Method obj = new Method();
        obj.first();
        obj.first(2);
        obj.first(45, 5);
    }
}