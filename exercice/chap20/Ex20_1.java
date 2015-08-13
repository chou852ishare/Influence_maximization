public class Ex20_1 {

    public static int add(int a, int b) {
        int r = 0; // addition result
        int f = 1; // indicate whether to carry bit
        while (f != 0) {
            r = a | b;
            f = a & b;
            r = r & (~f);   // 1b+1b=10b, make lower bit 0
            f = f << 1;     // carry bit, make higher bit 1
            a = r;
            b = f;
        }
        return r;
    }

    public static void main(String[] args) {
        int[] a = {1, 42, 73, 44, 35, 80, 9, 97, 6, 43, 243};
        for (int i = 0; i < a.length-1; i++) {
            System.out.println(String.format("************** %s **************", i));
            System.out.println(a[i] + "+" + a[i+1] + "=" + add(a[i], a[i+1]));
            System.out.println(a[i] + "+" + a[i+1] + "=" + (a[i]+a[i+1]));
        }
    }

}
