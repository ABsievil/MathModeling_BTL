# MathModeling_BTL  // need to adjust
code assigment for Semester 231

**using instruction git and github:
BASIC INSTRUCTION:

* git init        tạo repository trong máy
* git clone       lấy trên mạng về
* git pull        đồng bộ trên mạng về  // là combine của git fetch và git merge

* git add <name file> & git add .  add zô local repo
* git commit     lưuu
* git push       đồng bộ từ máy lên mạng

* git log/git status        check trạng thái
* git log —decorate —graph —oneline
-------------------------------------------------------------------
ADVANCE INSTRUCTION:

git checkout -b <tên nhánh mới> <nhánh gốc>      //add branch
git checkout <tên nhánh>                         //move to tên nhánh
$ git branch                                     //xem nhánh con của nhánh đang ở hiện tại 

===================================================================
**manipulate commands:
 login
B1: login to git server
*ban đầu: git config --global user.name "your name"
         git config --global user.email ..@..
note:Only use for the first login
-------------------------------------------------------------------
add new members for project:
B1:mở cmd của git lên vị trí cần lưu repo
B2:git clone <link project> 
B3: git remote add origin (thêm link project vào đây) 
-------------------------------------------------------------------
 push code
git init                               -khởi tạo repo tại máy chủ
git remote add origin (thêm link project vào đây)                      //Only use for the first login
git status                             -check file chưa add
git add <name file> or git add .
git commit -m "your note"        -lưu
git push -u origin <branch>              -add lên github
!note: khi push file lên github nhưng file trên github chưa được pull xuống, git sẽ báo lỗi: hint: (e.g., 'git pull ...') before pushing again.
khắc phục: ép buộc git push file từ local lên bằng lệnh : git push --force origin master
-------------------------------------------------------------------
pull code
cách 1:git pull                               -kéo xuống đồng bộ với máy chủ
cách 2:git fetch + git merge                  //cấu trúc lệnh ở ADVANCE INSTRUCTION:

-------------------------------------------------------------------
Rebase code: giả sử có nhánh cha dev và nhánh con login, muốn add commits trong login vào dev
B1:git pull                                      //pull new version for dev
B2: git checkout login                           //move to login branch
git rebase <dev>          //đem những commits bên trong nhánh login và áp dụng lại vào sau commit mới nhất trong dev
-------------------------------------------------------------------
Merge code:  //merge nhánh chính với nhánh gốc, giả sử có nhánh gốc là dev và nhánh con là login
B1: git status                         //đảm bảo đang ở nhánh dev, nếu không thực hiện lệnh git checkout dev
B2: git fetch                          //nạp code để đảm bảo version cả login và dev là version mới nhất
B3:git pull                            //pull code từ github về 
B4:git merge <branch name>             //branch name = login 

