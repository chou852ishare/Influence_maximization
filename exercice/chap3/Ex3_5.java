import java.lang.StringBuilder;

public class Ex3_5 {
    /*
    * implement a queue using two stacks
    */
    MyStack s1 = new MyStack();
    MyStack s2 = new MyStack();
    
    public void add(int value) {
        // push new node to s1
        s1.push(value);
    }

    public int remove() {
        if (s2.empty()) {
            moveS1ToS2();
        }
        return s2.pop();
    }

    public int peek() {
        if (s2.empty()) {
            moveS1ToS2();
        }
        return s2.peek();
    }

    private void moveS1ToS2() {
        while (!s1.empty()) {
            s2.push(s1.pop());
        }
    }

    @Override 
    public String toString() {
        StringBuilder sb1 = new StringBuilder();
        StringBuilder sb2 = new StringBuilder();
        sb1.append(s1.toString());
        sb2.append(s2.toString());
        sb2.reverse();
        return sb2.toString() + sb1.toString();
    }

    public static void main(String[] args) {
        Ex3_5 ex35 = new Ex3_5();
        ex35.add(1);
        ex35.add(2);
        ex35.add(3);
        ex35.add(4);
        System.out.println(ex35);
        ex35.remove();
        System.out.println(ex35);
        ex35.add(2);
        ex35.add(3);
        ex35.add(4);
        System.out.println(ex35);
        ex35.remove();
        System.out.println(ex35);
        ex35.remove();
        System.out.println(ex35);
        ex35.remove();
        System.out.println(ex35);
        ex35.remove();
        System.out.println(ex35);
    }
}
