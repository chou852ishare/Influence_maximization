import java.util.Scanner;

public class Ex1_3 {
    public char[] string2CharArr(String s) {
        char[] chars = new char[s.length()];
        for (int i = 0; i < s.length(); i++) {
            chars[i] = s.charAt(i);
        }
        return chars;
    }

    public void uniq(char[] s) {
        int ulen = 1;
        int ui   = 0;
        for(int oi = 1; oi < s.length; oi++) {
            for (ui = 0; ui < ulen; ui++) {
                if (s[ui] == s[oi]) {
                    break;
                }
            }
            if (ui == ulen) {
                s[ulen] = s[oi];
                ulen++;
            }
        }
        s[ulen] = '$';
    } 


    public static void main(String[] args) {
        System.out.println("Please input a string...");
        Ex1_3 ex13  = new Ex1_3();
        Scanner scr = new Scanner(System.in);
        for (int i = 0; i < 5; i++) {
            String s    = scr.nextLine();
            char[] cs   = ex13.string2CharArr(s);
            ex13.uniq(cs);
            System.out.println("****************************");
            System.out.println(s + "\toriginal");
            System.out.print(cs); System.out.println("\tuniq");
        }
    }
}
