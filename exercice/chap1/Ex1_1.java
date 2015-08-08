import java.util.HashSet;

public class Ex1_1 {
    int[] feq;
    HashSet<Character> charSet;

    public boolean testAscii(String s) {
        for(int i = 0; i < s.length(); i++) {
            int ci = s.charAt(i);
            this.feq[ci]++;
            if(this.feq[ci] > 1)
                return false;
        }
        return true;
    }

    public boolean testHashSet(String s) {
        for(int i = 0; i < s.length(); i++) {
            Character c = s.charAt(i);
            if (this.charSet.contains(c))
                return false;
            else 
                this.charSet.add(c);
        }
        return true;
    }

    public void setFeq() {
        this.feq = new int[127];
    }

    public void setCharSet() {
        this.charSet = new HashSet<Character>();
    }


    public static void main(String[] args) {
        //System.out.println("Please input some strings.");
        
        System.out.println("string\ttestByAscii\ttestByHash");
        Ex1_1 ex11 = new Ex1_1();
        for(String s: args) {
            ex11.setFeq();
            ex11.setCharSet();
            boolean flag1 = ex11.testAscii(s);
            boolean flag2 = ex11.testHashSet(s);
            System.out.println(s + "\t" + flag1 + "\t" + flag2);
        }
    }
}
