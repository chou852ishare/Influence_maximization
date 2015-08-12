import java.util.Scanner;

public class Ex5_1 {
    
    /********************
     *
     * get number of valid bits of integer n
     */
    public int getNum(int n) {
        int i;
        for ( i = 0; i < 32; i++) {
            n = n >> 1;
            if (n == 0) break;
        }
        return i;
    }

    public static void main(String[] args) {
        Scanner scan = new Scanner(System.in);
        System.out.println("please input an integer...");
        System.out.println("N = ");
        int N = scan.nextInt();
        System.out.println("M = ");
        int M = scan.nextInt();
        System.out.println("please input an offset...");
        System.out.println("i = ");
        int i = scan.nextInt();
        System.out.println("N = " + N + " = 0b" + Integer.toBinaryString(N));
        System.out.println("M = " + M + " = 0b" + Integer.toBinaryString(M));
        System.out.println("i = " + i);
        System.out.println("");
        
        Ex5_1 ex51 = new Ex5_1();
        int nn = ex51.getNum(N);
        int nm = ex51.getNum(M);
        if (i+nm > nn) {
            System.out.println("Error! N is not long enough.");
            return;
        }
        int M1 = M << i;
        int N1 = (Integer.MAX_VALUE >> (31-nm-1)) << i;
        N  = (N & (~N1)) + M1;
        System.out.println("M1= 0b" + Integer.toBinaryString(M1));
        System.out.println("N1= 0b" + Integer.toBinaryString(N1));
        System.out.println("N = 0b" + Integer.toBinaryString(N));
    }
}
