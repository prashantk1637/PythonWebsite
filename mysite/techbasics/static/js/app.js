function fetch_api(method,url,json_data,callback)
{
    var response="";
    var xhr = new XMLHttpRequest();
    xhr.open(method,url, true);
    xhr.setRequestHeader("Content-type","application/json charset=utf-8");
    xhr.onload = function ()
    {
        if (xhr.readyState == 4 && xhr.status == 200)
        {
           callback(xhr.responseText);
        }
    };
    xhr.send(json_data);

    return response;
}
function send_data(data)
{
    var list=data.split(":");
    var divid=list[0];
    var id=list[1];
    var answeritem = document.getElementById("center-div").getElementsByClassName("answer")[divid-1];
    var anchor = document.getElementById("center-div").getElementsByClassName("update")[divid-1];
    const randomid = Math.random().toString(36).substring(2,15);
    answeritem.id=randomid;
    anchor.href="#"+randomid;
    answeritem.contentEditable="false";
    var divvalue  = answeritem.innerHTML;
    var div_rawdata = String(divvalue);
    div_rawdata=div_rawdata.replace(/@@/g,"<")
    div_rawdata=div_rawdata.replace(/##/g,">")
    div_rawdata=div_rawdata.replace(/%%/g,"</")
    div_rawdata=div_rawdata.replace(/<br>/g, "\r\n");
    div_rawdata=div_rawdata.replace(/<code>/g,"<keyword>")
    div_rawdata=div_rawdata.replace(/<\/code>/g,"</keyword>")
    div_rawdata=div_rawdata.replace(/<pre>/g,"<code>")
    div_rawdata=div_rawdata.replace(/<\/pre>/g,"</code>")
    var url = "https://techbasics.pythonanywhere.com/api/update/"+id
    var dict_data = {};
    dict_data.id = id;
    dict_data.value=div_rawdata
    var json = JSON.stringify(dict_data);
    fetch_api("PUT",url,json,mycallback);
}
function edit_data(divid)
{
    var answeritem = document.getElementById("center-div").getElementsByClassName("answer")[divid-1];
    var anchor = document.getElementById("center-div").getElementsByClassName("edit")[divid-1];
    const randomid = Math.random().toString(36).substring(2,15);
    answeritem.id=randomid;
    anchor.href="#"+randomid;
    answeritem.contentEditable="true";
}
function mycallback(data)
{
    data=data.replace(/#/g,"<br>")
    document.getElementById("demo").innerHTML=data;
    document.getElementById("runningbtn").style.display="none"
    document.getElementById("runbtn").style.display="block";
}
var code_inp=""
var lang_inp=""
function runApi()
{
    document.getElementById("runbtn").style.display="none";
    document.getElementById("runningbtn").style.display="block"
    var lang = document.getElementById("language").value;
    var code = document.getElementById("code").value;

    var code_inp=document.getElementById("code").value;
    localStorage.setItem("code_key", code_inp);
	var s_v=document.getElementById("language");

	lang_inp= s_v.options[s_v.selectedIndex].value;
	localStorage.setItem("lang_key", lang_inp);

    var url = "https://techbasics.pythonanywhere.com/run-code";
    var dict_data = {};
    dict_data.language=lang;
    dict_data.code=code;
    var json = JSON.stringify(dict_data);
    fetch_api("POST",url,json,mycallback);

}

function loadBody()
{
    size=screen.width;
    ld= document.getElementById("left-div");
    cd=document.getElementById("center-div");
    rd= document.getElementById("right-div");
    ldb=document.getElementById("leftDivBtn");
    if (size<500)
    {
        cd.style.width="100%";
        ld.style.width="0px";
        ld.style.padding="0px"
         ld.style.border="1px solid black";
         ld.style.borderRadius="5px";
         rd.style.display="none";
         ldb.style.display="block";

    }
    else{

        cd.style.width="60%";
        cd.style.marginLeft="20%";
       }
}
function show_left_div()
{
     size=screen.width;
     ld= document.getElementById("left-div");
     cd=document.getElementById("center-div");
     ldb=document.getElementById("leftDivBtn");

     if (size<500)
     {

        ld.style.width="70%";
        ld.style.transition="width 0.5s"
        ld.style.position="fixed";
        ld.style.background="white";
        ld.style.border="1px solid black";
        ldb.innerHTML="&#9194;"
        ldb.setAttribute("onclick","hide_left_div()")
     }
     else{
          ld.style.width="20%";
          cd.style.marginLeft="0%";
     }
}
function hide_left_div(){
    size=screen.width;
    ld= document.getElementById("left-div");
     cd=document.getElementById("center-div");
     ldb=document.getElementById("leftDivBtn");
     if(size<500)
     {
         ld.style.width="0px";
         ld.style.padding="0px";
         ld.style.border="none";
         ldb.innerHTML="&#9193;"
         ldb.setAttribute("onclick","show_left_div()")
     }
     else{

         cd.style.marginLeft="20%";
     }

}
function check_uncheck(index)
{
 var checkBox = document.getElementById("center-div").getElementsByClassName("checkboxcls")[index-1];
  var qitem = document.getElementById("center-div").getElementsByClassName("question")[index-1];
  var aitem = document.getElementById("center-div").getElementsByClassName("answer")[index-1];
  var mar = document.getElementById("center-div").getElementsByClassName("mark-as-read")[index-1];

  if (checkBox.checked == true)
  {
    //qitem.style.display = "none";
    aitem.style.display = "none";
    mar.style.color="green"
  }
  else
  {
    //qitem.style.display = "block";
    aitem.style.display = "block";
    mar.style.color="black"
  }

}