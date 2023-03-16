<template>
  <div class="hello">
    <h1>{{ msg }}</h1>
    <div class="form">
        <el-row>
          <el-col :span="22" class="input">
            <el-input v-model="input" placeholder="请输入根目录"></el-input>
          </el-col>
          <el-col :span="2" class="button" >
            <el-button type="primary" round @click="submit">提交</el-button>
          </el-col>
        </el-row>  
    </div>
    <div class="scanningRes" style="display:none">
        <h1>Suspected_node_list</h1>
        <div class="nodeList"></div>
        <!-- <h1>Manual Marking VS Program Marking</h1>
        <div class="missed"></div>
        <h1>Accracy</h1>
        <div class="accuracy"></div> -->
        </div>
  </div>
</template>

<script>
import axios from "axios"
export default {
  name: 'HelloWorld',
  data () {
    return {
      input:'',
      msg: 'Python program scan',
      serverResponse:{}
    }
  },
  methods:{
    submit(){
      var that = this;
      // 对应 Python 提供的接口，这里的地址填写下面服务器运行的地址，本地则为127.0.0.1，外网则为 your_ip_address
      const path = "http://127.0.0.1:5000/scan";
      if(that.input!=''){
        axios
        .post(path,{source:that.input}
      )
        .then(function(response) {
          // 这里服务器返回的 response 为一个 json object，可通过如下方法需要转成 json 字符串
          // 可以直接通过 response.data 取key-value
          // 坑一：这里不能直接使用 this 指针，不然找不到对象
          that.serverResponse = response.data;
          // 坑二：这里直接按类型解析，若再通过 JSON.stringify(msg) 转，会得到带双引号的字串
          console.log(that.serverResponse)
          that.displayTheScannningRes();
        })
        .catch(function(error) {
          alert("Error " + error);
        });
      }
    },
    displayTheScannningRes(){
      var scanningRes = document.getElementsByClassName("scanningRes")[0]
      console.log(this.serverResponse)
      scanningRes.style.display = 'block'
      // 增加 项目扫描结果
      var nodeListNode = scanningRes.getElementsByClassName("nodeList")[0]
      var nodeList = this.serverResponse.result.missed.suspected_node_list
      for(var i=0;i<nodeList.length;i++){
        var line_out = document.createElement("p")
        line_out.innerHTML = nodeList[i]
        nodeListNode.appendChild(line_out)
      }
    
      // 增加 准确率
      // var accuracyNode = document.getElementsByClassName("accuracy")[0]
      // var location_num = this.serverResponse.accuracy.location_num
      // var recall_accurate = this.serverResponse.accuracy.recall_accurate
      // var recall_location = this.serverResponse.accuracy.recall_location
      // var line_one = document.createElement("h3")
      // var line_sec = document.createElement("h3")
      // line_one.innerHTML="查全率: "+ "行数类型都命中 "+recall_accurate+ "   "+ "行数命中 "+recall_location+"   "+"人工标注个数 "+location_num+"   "+ "比率 "+recall_location / location_num
      // line_sec.innerHTML="查准率: "+ "行数类型都命中 "+recall_accurate+ "   "+ "行数命中 "+recall_location+ "    "+ "项目标注个数 "+nodeList.length+ "    "+"比率 "+
      //     recall_location / nodeList.length
      
      // accuracyNode.appendChild(line_one)
      // accuracyNode.appendChild(line_sec)
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.input{
  text-align: right;
}
.button{
  text-align: left;
}
.form{
  padding-left: 30%;
  padding-right: 30%;
}
.scanningRes{
  padding-left: 10%;
  text-align: left;
}
</style>
