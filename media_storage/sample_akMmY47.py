n = int(input())#○位置1~3
m = int(input())#シャッフル回数
cup = [0, 0, 0]
cup[n-1] = 1#丸の付いたカップの要素は1とする

#シャッフル
for i in range(m):
    a, b=map(int,input().split())
    cup[a-1], cup[b-1] = cup[b-1], cup[a-1]

print(cup.index(1)+1)
