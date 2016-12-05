> Linux + hexo + python + github运行环境可以直接clone工程到本地,将工程中的文件拷贝到hexo博客的根目录,例如/home/hexo/blog下,修改expect.sh中的用户名密码为自己的github的用户名密码,随后运行python deploy.py,输入新浪微博用户名和密码就可以将博客一键部署到github,并将博文中的图片替换为新浪图床的图片,示例网站:http://trytofix.com. 其他环境的用户,可根据下面对每个文件的解释,各取所需.

> Linux 需要安装expect, `sudo apt-get install expect`

### weibo_util.py 用来模拟登陆微博,将本地图片上传到新浪图床,并获取图床的链接.
``` python
if __name__ == '__main__':
    print get_image('/home/q/hexo/blog/source/img/angular-remove-table-item.jpg')

添加了optparser,通过python weibo_util.py -f image_path -u weibo_username -p weibo_password可以传入微博的用户名和密码，避免交互式的输入．
```
修改get_image()中的路径为本机电脑上的路径,随后python weibo_util.py就可以查看效果,第一次使用,会提示输入新浪微博的用户名和密码,程序运行成功后返回图床的url地址.

### install.sh 一个简单的发布脚本,集成了hexo发布的三个步骤: clean, generate, deploy,注意最后一行的expect.sh,介绍在下面.
``` shell
#!/bin/bash

hexo clean
hexo g
./expect.sh
```

### expect.sh 部署hexo到github时,需要输入用户名和密码,使用expect可以自动输入用户名和密码,将
``` shell
set user yourusername
set pass yourpassword
```
替换为自己的github的用户名和密码.
> 如果不需要将博客部署到github,请在install.sh中注释./expect.sh或替换为hexo d

### deploy.py部署hexo博客
- 将_posts下的文章备份
- 遍历所有的文章,找到`![image_alt](image_url)`标准markdown格式的image_url,其中image_url的格式应为'/img/xxx.jpg',位于source/img下
- 通过weibo_util获取改图片的图床地址并替换
- 执行install.sh,生成图片地址为图床地址的博客页面
- 将文章备份替换回来,_posts下的文章中的图片仍为markdown格式.

> 为了避免每次部署时,都生成新的图床url(浪费资源可耻,感谢新浪无私的没有做防盗链限制),在部署时,将图片做md5计算,将md5与新浪图床url存入map,最后使用json持久化到文件中(image.db),每次部署先查看md5是否存在map中,如果存在,则直接取md5对应的value值,否则,获取图床地址并存入image.db.

### image.db存放图片md5与图床url对应关系的json数据库


> 更多内容请访问:http://trytofix.github.io/2016/04/06/hexo%E4%BD%BF%E7%94%A8%E6%96%B0%E6%B5%AA%E5%BE%AE%E5%8D%9A%E5%9B%BE%E5%BA%8A%E8%87%AA%E5%8A%A8%E9%83%A8%E7%BD%B2/

