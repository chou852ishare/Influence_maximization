import java.util.Scanner;
import java.lang.StringBuilder;

public class Ex5_2 {
    public static void main(String[] args) {
        Scanner scan = new Scanner(System.in);
        System.out.println("please input a decimal number...");
        float n = scan.nextFloat();
        // deal with only the decimal part
        StringBuilder sb = new StringBuilder();
        float nd = n - ((int) n);
        while (nd != 0) {
            int i = (int) (nd*2);
            sb.append(i);
            nd = nd*2 - i;
        }
        System.out.println("n = " + n + " = 0b" + sb.toString());
    }
}
