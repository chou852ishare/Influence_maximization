import java.lang.StringBuilder;

public class Ex3_1 {
    /* 
    * use a single array to implement three stacks
    */
    
    SNode[] array = new SNode[256];
    SNode top1, top2, top3;
    int head = 0;  // head is the index to first empty position in array
    
    private void updateHead() {
        for (int i = 0; i < 256; i++) {
            if (array[i] == null) {
                head = i;
                break;
            }
        }
    }
    
    public void push1(int value) {
        SNode node  = array[head];
        node        = new SNode(value);
        node.prev   = top1;
        top1        = node;
        updateHead();
    }

    public void push2(int value) {
        SNode node  = array[head];
        node        = new SNode(value);
        node.prev   = top2;
        top2        = node;
        updateHead();
    }

    public void push3(int value) {
        SNode node  = array[head];
        node        = new SNode(value);
        node.prev   = top3;
        top3        = node;
        updateHead();
    }

    public void pop1() {
        SNode otop = top1;
        top1 = top1.prev;
        otop = null;
        updateHead();
    }
    
    public void pop2() {
        SNode otop = top2;
        top2 = top2.prev;
        otop = null;
        updateHead();
    }
    
    public void pop3() {
        SNode otop = top3;
        top3 = top3.prev;
        otop = null;
        updateHead();
    }
    
    @Override
    public String toString() {
        // toString stack1
        StringBuilder sb1 = new StringBuilder();
        for (SNode curr = top1; curr != null; curr = curr.prev) {
            sb1.append(curr.value);
        }
        sb1.reverse();
        // toString stack2
        StringBuilder sb2 = new StringBuilder();
        for (SNode curr = top2; curr != null; curr = curr.prev) {
            sb2.append(curr.value);
        }
        sb2.reverse();
        // toString stack3
        StringBuilder sb3 = new StringBuilder();
        for (SNode curr = top3; curr != null; curr = curr.prev) {
            sb3.append(curr.value);
        }
        sb3.reverse();
        return sb1.toString() + "\n" + sb2.toString() + "\n" + sb3.toString();
    }

    public static void main(String[] args) {
        Ex3_1 ex31 = new Ex3_1();
        ex31.push1(1);
        ex31.push1(3);
        ex31.push1(8);
        ex31.push2(9);
        ex31.push2(5);
        ex31.push3(4);
        ex31.push3(4);
        System.out.println(ex31);
        ex31.pop1();
        ex31.pop1();
        ex31.pop2();
        ex31.pop3();
        System.out.println(ex31);
    }
}
