import java.util.Arrays;
import java.util.Comparator;

public class Ex9_2 implements Comparator<String> {

    @Override
    public int compare(String s1, String s2) {
        // check anagrams
        char[] c1 = new char[s1.length()];
        char[] c2 = new char[s2.length()];
        s1.getChars(0, s1.length(), c1, 0);
        s2.getChars(0, s2.length(), c2, 0);
        Arrays.sort(c1);
        Arrays.sort(c2);
        // if anagrams, return 0
        if (Arrays.equals(c1, c2)) return 0;
        // else return compareTo
        return (String.copyValueOf(c1)).compareTo(String.copyValueOf(c2));
    }

    @Override 
    public boolean equals(Object obj) {
        return false;
    }

    public static void main(String[] args) {
        String[] ss = {"abc", "bcd", "bca", "ef", "cba", "bdc", "efg", "eg", "fe"};
        System.out.println(Arrays.asList(ss)); 
        Arrays.sort(ss);
        System.out.println(Arrays.asList(ss)); 

        Ex9_2 c92 = new Ex9_2();
        Arrays.sort(ss, c92);
        System.out.println(Arrays.asList(ss)); 
    }
}
