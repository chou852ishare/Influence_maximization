import java.util.Scanner;

public class Ex19_4 {
    
    public int max(int a, int b) {
        int m = 0;
        while (a > 0 || b > 0) {
            a--;
            b--;
            m++;
        }
        return m;
    }

    public static void main(String[] args) {
        System.out.println("please enter two numbers...");
        Scanner scan = new Scanner(System.in);
        int a = scan.nextInt();
        int b = scan.nextInt();
        System.out.println("a = " + a + " b = " + b);

        Ex19_4 ex194 = new Ex19_4();
        System.out.println("max = " + ex194.max(a, b));
    }
}
