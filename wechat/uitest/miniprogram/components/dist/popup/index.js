import zIndex from"../behaviors/zIndex";import validator from"../behaviors/validator";Component({behaviors:[zIndex,validator],externalClasses:["l-bg-class","l-panel-class","1-class"],properties:{show:{type:Boolean,value:!1},animation:{type:Boolean,value:!0},transition:{type:Boolean,value:!0},contentAlign:{type:String,value:"",options:["","top","right","left","bottom","center"]},direction:{type:String,value:"center",options:["top","right","left","bottom","center"]},locked:{type:Boolean,value:!1},opacity:{type:Number,value:.4}},attached(){this._init()},pageLifetimes:{show(){this._init()}},data:{status:"show"},methods:{_init(){wx.lin=wx.lin||{},wx.lin.showPopup=t=>{const{zIndex:e=99,animation:o=!0,contentAlign:a="center",locked:i=!1}={...t};this.setData({zIndex:e,animation:o,contentAlign:a,locked:i,show:!0})},wx.lin.hidePopup=()=>{this.setData({status:"hide"}),setTimeout(()=>{this.setData({show:!1})},300)}},doNothingMove(){},doNothingTap(){},onPupopTap(){!0!==this.data.locked&&(this.data.show?(this.setData({status:"hide"}),setTimeout(()=>{this.setData({show:!1,status:"show"})},300)):this.setData({show:!0,status:"show"})),this.triggerEvent("lintap",!0,{bubbles:!0,composed:!0})}}});