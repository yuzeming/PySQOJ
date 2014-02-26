【Conf.json 必须】
[
    ["cowcheck.in","cowcheck.out"], #输入文件名 输出文件名
    null, #比较方式 设为null 使用默认比较方式 也可以使用 "Diff $(IN) $(OUT) $(ANS)" ,Diff文件必须存在
    [	#数据配置
        [30,	#该数据组的分数
			["cowcheck.1.in","cowcheck.1.out",1,128],	#输入文件 输出文件 时间(秒) 内存(兆)
			["cowcheck.2.in","cowcheck.2.out",1,128],
			["cowcheck.3.in","cowcheck.3.out",1,128]
		],
        [30,["cowcheck.4.in","cowcheck.4.out",1,128],["cowcheck.5.in","cowcheck.5.out",1,128],["cowcheck.6.in","cowcheck.6.out",1,128]],
		[40,["cowcheck.7.in","cowcheck.7.out",1,128],["cowcheck.8.in","cowcheck.8.out",1,128],["cowcheck.9.in","cowcheck.9.out",1,128],["cowcheck.10.in","cowcheck.10.out",1,128]]
    ]
]
#不得有多余逗号和字符，不得有注释
【Makefile 可选】
如果存在 系统将在此目录执行 make 
用于编译自定义比较器等。

【prob.hmtml solve.html 可选】
系统可以从这两个文件导入题面和题解
注意题面和题解在WEB界面修改后不会更新到压缩包内

【打包方法】
把所有文件打包成【ZIP】即可。ZIP文件应【直接】包含Conf.json等文件。
上传到WEB界面后会自动更新所有评测端数据

【自定义比较器】
输出到标准输出，不需要文件
格式为
0.4 部分正确
请使用UTF-8编码输出，否则无法显示

系统会先在数据目录下查证，然后到JUDGE/cmp下查找。

【安装方法】
请先安装Python 2.7
使用管理员权限运行 setup.cmd

