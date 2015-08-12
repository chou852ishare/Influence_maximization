import java.util.ArrayList;
import java.util.Scanner;

public class Ex8_2 {

    public ArrayList<String> enumeratePath(int m, int n) {
        ArrayList<String> path = new ArrayList<String>();
        if (m > 0 && n > 0) {
            // go right or down
            for (String rp : enumeratePath(m, n-1)) // go right
                path.add("-" + rp);
            for (String lp : enumeratePath(m-1, n)) // go down
                path.add("|" + lp);
            return path;
        } else {
            // reach boundary
            path.add("");
            return path;
        }
    }
    
    public static void main(String[] args) {
        System.out.println("please input N...");
        Scanner scan = new Scanner(System.in);
        int N = scan.nextInt();
        System.out.println("N = " + N);
        Ex8_2 ex82 = new Ex8_2();
        for (String p : ex82.enumeratePath(N, N)) 
            System.out.println(p);
    }
}
