public class Ex14_1 {
    int a = 1;

    public int getA() {
        return this.a;
    }

    private Ex14_1() {
    }

    public Ex14_1(int a) {
        this.a = a;
    }

    public static void main(String[] args) {
        Ex14_1 ex141 = new Ex14_1();
        System.out.println("a = " + ex141.getA());
    }
}
