import java.lang.StringBuilder;
import java.util.Scanner;

public class Ex1_2 {
    int front, end;

    public String reverse(String s) {
        front   = 0;
        end     = 0;
        StringBuilder sb = new StringBuilder();
        sb.append(s);
        for (int i = 0; i < s.length(); i++) {
            end++;
        }
        end--;
        while (front < end) {
            char temp = sb.charAt(front);
            sb.setCharAt(front, sb.charAt(end));
            sb.setCharAt(end, temp);
            front++;
            end--;
        }
        return sb.toString();
    }

    public static void main(String[] args) {
        System.out.println("Please input a string...");
        Scanner scr = new Scanner(System.in);
        for (int i = 0; i < 3; i++) {
            String s    = scr.nextLine();
            String rs   = new StringBuilder().append(s).reverse().toString(); 
            Ex1_2 ex12  = new Ex1_2();
            String rs1  = ex12.reverse(s);
            System.out.println("original\trsByBuilder\trsByAlgo");
            System.out.println(s + "\t" + rs + "\t" + rs1);
            System.out.println("***************************************");
        }
    }

}
