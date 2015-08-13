import java.util.Scanner;

public class Ex19_1 {

    public void swap(Integer a, Integer b) {
        int ai = a;
        int bi = b;
        ai = bi - ai; // ai = delata
        bi = bi - ai; // bi = a
        ai = bi + ai; // ai = b
        System.out.println("a = " + ai + ", b = " + bi);
    }
    
    public static void main(String[] args) {
        System.out.println("please input a and b...");
        Scanner scan = new Scanner(System.in);
        Integer a = scan.nextInt();
        Integer b = scan.nextInt();
        System.out.println("a = " + a + ", b = " + b);

        System.out.println("*************** swapping ***************");
        Ex19_1 ex191 = new Ex19_1();
        ex191.swap(a, b);
    }
}
