import java.util.Scanner;

public class Ex8_1 {

    /******************
     * compute Fibonacci number recursively
     */
    public int getNthFibonacci(int n) {
        if (n == 0) return 0;
        if (n == 1) return 1;
        int fibonacci = getNthFibonacci(n - 1) + getNthFibonacci(n - 2);
        System.out.println(n + "\t" + fibonacci);
        return fibonacci;
    }

    /******************
     * compute Fibonacci number iteratively
     */
    public void getFibonacci(int n) {
        int fibonacci0 = 0;
        int fibonacci1 = 1;
        int fibonacci  = 0;
        System.out.println("************** iterative fibonacci ************");
        for (int i = 2; i <= n; i++) {
            fibonacci  = fibonacci0 + fibonacci1;
            fibonacci0 = fibonacci1;
            fibonacci1 = fibonacci;
            System.out.println(i + "\t" + fibonacci);
        }
    }
    
    public static void main(String[] args) {
        System.out.println("please input an integer to set n...");
        Scanner scan = new Scanner(System.in);
        int n = scan.nextInt();
        Ex8_1 ex81 = new Ex8_1();
        System.out.println("************** recursive fibonacci ************");
        ex81.getNthFibonacci(n);
        ex81.getFibonacci(n);
    }
}
