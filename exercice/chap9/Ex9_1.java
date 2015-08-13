import java.util.ArrayList;
import java.util.Arrays;
import java.util.Scanner;
import java.util.Collections;

public class Ex9_1 {
    public static ArrayList<Integer> strArr2IntList(String[] ss) {
        ArrayList<Integer> a = new ArrayList<Integer>(ss.length);
        for (int i = 0; i < ss.length; i++) {
            a.add(Integer.parseInt(ss[i]));
        }
        return a;
    }

    public static Integer[] setC(Integer[] a, Integer[] b) {
        Integer[] c = new Integer[a.length + b.length];
        for (int i = 0; i < a.length; i++) 
            c[i] = a[i];
        for (int i = 0; i < b.length; i++) 
            c[i + a.length] = b[i];
        return c;
    }

    public void bubbleSort(Integer[] a, int n) {
        for (int j = n; j < a.length; j++) {
            int i = j;
            while (a[i] < a[i-1] && i > 0) {
                swap(a, i, i-1);
                i--;
            }
        }
    }

    public void mergeSort(Integer[] a, Integer[] b) {
        int i = 0; 
        for (int j = 0; j < a.length; j++) {
            // compare a[j] with b[i]
            if (a[j] > b[i]) {
                onePositionRight(a, j);
                a[j] = b[i];
                i++;
            }
        }
        // add very large b elements directly to the end of a
        for (int k = i; k < b.length ; k++) {
            a[k - b.length + a.length] = b[k]; 
        }
    }

    private void onePositionRight(Integer[] a, int j) {
        for (int i = a.length - 1; i > j; i--) {
            a[i] = a[i - 1];
        }
    }

    private void swap(Integer[] a, int i, int j){
        Integer temp;
        temp = a[i];
        a[i] = a[j];
        a[j] = temp;
    }
    
    public static void main(String[] args) {
        System.out.println("please input array1...");
        Scanner scan = new Scanner(System.in);
        String[] ss1 = scan.nextLine().split(" ");
        ArrayList<Integer> a1 = strArr2IntList(ss1);
        Collections.sort(a1);
        System.out.println("a = " + a1);

        System.out.println("please input array2...");
        scan = new Scanner(System.in);
        String[] ss2 = scan.nextLine().split(" ");
        ArrayList<Integer> a2 = strArr2IntList(ss2);
        Collections.sort(a2);
        System.out.println("b = " + a2);

        Ex9_1 ex91 = new Ex9_1();
        Integer[] a = a1.toArray(new Integer[a1.size()]);
        Integer[] b = a2.toArray(new Integer[a2.size()]);
        Integer[] c = setC(a, b);
        System.out.println("c = " + Arrays.asList(c));
        ex91.bubbleSort(c, a.length);
        System.out.println("c = " + Arrays.asList(c));
        c = setC(a, b);
        ex91.mergeSort(c, b);
        System.out.println("c = " + Arrays.asList(c));
    }
}
