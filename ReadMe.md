��Conf.json ���롿
[
    ["cowcheck.in","cowcheck.out"], #�����ļ��� ����ļ���
    null, #�ȽϷ�ʽ ��Ϊnull ʹ��Ĭ�ϱȽϷ�ʽ Ҳ����ʹ�� "Diff $(IN) $(OUT) $(ANS)" ,Diff�ļ��������
    [	#��������
        [30,	#��������ķ���
			["cowcheck.1.in","cowcheck.1.out",1,128],	#�����ļ� ����ļ� ʱ��(��) �ڴ�(��)
			["cowcheck.2.in","cowcheck.2.out",1,128],
			["cowcheck.3.in","cowcheck.3.out",1,128]
		],
        [30,["cowcheck.4.in","cowcheck.4.out",1,128],["cowcheck.5.in","cowcheck.5.out",1,128],["cowcheck.6.in","cowcheck.6.out",1,128]],
		[40,["cowcheck.7.in","cowcheck.7.out",1,128],["cowcheck.8.in","cowcheck.8.out",1,128],["cowcheck.9.in","cowcheck.9.out",1,128],["cowcheck.10.in","cowcheck.10.out",1,128]]
    ]
]
#�����ж��ය�ź��ַ���������ע��
��Makefile ��ѡ��
������� ϵͳ���ڴ�Ŀ¼ִ�� make 
���ڱ����Զ���Ƚ����ȡ�

��prob.hmtml solve.html ��ѡ��
ϵͳ���Դ��������ļ�������������
ע������������WEB�����޸ĺ󲻻���µ�ѹ������

�����������
�������ļ�����ɡ�ZIP�����ɡ�ZIP�ļ�Ӧ��ֱ�ӡ�����Conf.json���ļ���
�ϴ���WEB�������Զ������������������

���Զ���Ƚ�����
�������׼���������Ҫ�ļ�
��ʽΪ
0.4 ������ȷ
��ʹ��UTF-8��������������޷���ʾ

ϵͳ����������Ŀ¼�²�֤��Ȼ��JUDGE/cmp�²��ҡ�

����װ������
���Ȱ�װPython 2.7
ʹ�ù���ԱȨ������ setup.cmd

