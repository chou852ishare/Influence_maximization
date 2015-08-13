import java.util.Arrays;
import java.util.Scanner;

public class Ex9_3 {

    public static Integer[] getIntArray(String s) {
        String[] ss = s.split(" ");
        Integer[] a = new Integer[ss.length];
        for (int i = 0; i < ss.length; i++) {
            a[i] = Integer.parseInt(ss[i]);
        }
        return a;
    }

    public static void rotate(Integer[] a, int n) {
        Integer[] temp = new Integer[n];
        for (int i = 0; i < n; i++) {
            temp[i] = a[i];
        }
        for (int i = n; i < a.length; i++) {
            a[i - n] = a[i];
        }
        for (int i = 0; i < n; i++) {
            a[i + a.length - n] = temp[i];
        }
    }

    public int search(Integer[] a, int e) {
        int index = 0;
        int i = 0; 
        int j = 0;
        int tail = a.length;
        while (tail > i) {
            j = (i + tail) / 2;
            // case 0: e == a[i] or a[j]
            if (e == a[i]) return i;
            if (e == a[j]) return j;
            // case 1: a[j] > a[i], no turning point
            if (a[j] > a[i]) {
                // subcase 1: e > a[j] or e < a[i], search second half
                if (e > a[j] || e < a[i]) {
                    i = j;
                    continue;
                }
                // subcase 2: e > a[i] and e < a[j], search first half
                if (e > a[i] && e < a[j]) {
                    tail = j;
                    continue;
                }
            }
            // case 2: a[j] < a[i], has turning point
            if (a[j] < a[i]) {
                // subcase 1: e < a[j] or e > a[i], search first half
                if (e < a[j] || e > a[i]) {
                    tail = j;
                    continue;
                }
                // subcase 2: e < a[i] and e > a[j], search second half
                if (e < a[i] && e > a[j]) {
                    i = j;
                    continue;
                }
            }
        }
        return index;
    }

    public static void main(String[] args) {
        System.out.println("please input some numbers");
        Scanner scan = new Scanner(System.in);
        Integer[] a = getIntArray(scan.nextLine());
        System.out.println("a = " + Arrays.asList(a));
       
        System.out.println("******** sorting *********");
        Arrays.sort(a);
        System.out.println("a = " + Arrays.asList(a));
        
        System.out.println("******** rotating *********");
        System.out.println("please enter n for rotate times...");
        int n = scan.nextInt();
        rotate(a, n);
        System.out.println("a = " + Arrays.asList(a));

        System.out.println("******** searching *********");
        System.out.println("please enter element e for search...");
        Ex9_3 ex93 = new Ex9_3();
        int e = scan.nextInt();
        int index = ex93.search(a, e);
        System.out.println("index = " + index);
        System.out.println("index = " + Arrays.binarySearch(a, e) + " using API.");
    }
}
