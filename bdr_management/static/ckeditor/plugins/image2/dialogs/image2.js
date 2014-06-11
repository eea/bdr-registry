﻿/*
 Copyright (c) 2003-2014, CKSource - Frederico Knabben. All rights reserved.
 For licensing, see LICENSE.md or http://ckeditor.com/license
*/
CKEDITOR.dialog.add("image2",function(j){function y(){var a=this.getValue().match(z);(a=!!(a&&0!==parseInt(a[1],10)))||alert(c["invalid"+CKEDITOR.tools.capitalize(this.id)]);return a}function J(){function a(a,b){d.push(i.once(a,function(a){for(var i;i=d.pop();)i.removeListener();b(a)}))}var i=p.createElement("img"),d=[];return function(d,b,c){a("load",function(){var a=A(i);b.call(c,i,a.width,a.height)});a("error",function(){b(null)});a("abort",function(){b(null)});i.setAttribute("src",d+"?"+Math.random().toString(16).substring(2))}}
function B(){var a=this.getValue();q(!1);a!==t.data.src?(C(a,function(a,d,b){q(!0);if(!a)return k(!1);g.setValue(d);h.setValue(b);r=d;s=b;k(D.checkHasNaturalRatio(a))}),l=!0):l?(q(!0),g.setValue(m),h.setValue(n),l=!1):q(!0)}function E(){if(e){var a=this.getValue();if(a&&(a.match(z)||k(!1),"0"!==a)){var b="width"==this.id,d=m||r,c=n||s,a=b?Math.round(c*(a/d)):Math.round(d*(a/c));isNaN(a)||(b?h:g).setValue(a)}}}function k(a){if(f){if("boolean"==typeof a){if(u)return;e=a}else if(a=g.getValue(),u=!0,
(e=!e)&&a)a*=n/m,isNaN(a)||h.setValue(Math.round(a));f[e?"removeClass":"addClass"]("cke_btn_unlocked");f.setAttribute("aria-checked",e);CKEDITOR.env.hc&&f.getChild(0).setHtml(e?CKEDITOR.env.ie?"■":"▣":CKEDITOR.env.ie?"□":"▢")}}function q(a){a=a?"enable":"disable";g[a]();h[a]()}var z=/(^\s*(\d+)(px)?\s*$)|^$/i,F=CKEDITOR.tools.getNextId(),G=CKEDITOR.tools.getNextId(),b=j.lang.image2,c=j.lang.common,K=(new CKEDITOR.template('<div><a href="javascript:void(0)" tabindex="-1" title="'+b.lockRatio+'" class="cke_btn_locked" id="{lockButtonId}" role="checkbox"><span class="cke_icon"></span><span class="cke_label">'+
b.lockRatio+'</span></a><a href="javascript:void(0)" tabindex="-1" title="'+b.resetSize+'" class="cke_btn_reset" id="{resetButtonId}" role="button"><span class="cke_label">'+b.resetSize+"</span></a></div>")).output({lockButtonId:F,resetButtonId:G}),D=CKEDITOR.plugins.image2,v=j.widgets.registered.image.features,A=D.getNatural,p,t,H,C,m,n,r,s,l,e,u,f,o,g,h,w,x=!(!j.config.filebrowserImageBrowseUrl&&!j.config.filebrowserBrowseUrl),I=[{id:"src",type:"text",label:c.url,onKeyup:B,onChange:B,setup:function(a){this.setValue(a.data.src)},
commit:function(a){a.setData("src",this.getValue())},validate:CKEDITOR.dialog.validate.notEmpty(b.urlMissing)}];x&&I.push({type:"button",id:"browse",style:"display:inline-block;margin-top:16px;",align:"center",label:j.lang.common.browseServer,hidden:!0,filebrowser:"info:src"});return{title:b.title,minWidth:250,minHeight:100,onLoad:function(){p=this._.element.getDocument();C=J()},onShow:function(){t=this.widget;H=t.parts.image;l=u=e=!1;w=A(H);r=m=w.width;s=n=w.height},contents:[{id:"info",label:b.infoTab,
elements:[{type:"vbox",padding:0,children:[{type:"hbox",widths:["100%"],children:I}]},{id:"alt",type:"text",label:b.alt,setup:function(a){this.setValue(a.data.alt)},commit:function(a){a.setData("alt",this.getValue())}},{type:"hbox",widths:["25%","25%","50%"],requiredContent:v.dimension.requiredContent,children:[{type:"text",width:"45px",id:"width",label:c.width,validate:y,onKeyUp:E,onLoad:function(){g=this},setup:function(a){this.setValue(a.data.width)},commit:function(a){a.setData("width",this.getValue())}},
{type:"text",id:"height",width:"45px",label:c.height,validate:y,onKeyUp:E,onLoad:function(){h=this},setup:function(a){this.setValue(a.data.height)},commit:function(a){a.setData("height",this.getValue())}},{id:"lock",type:"html",style:"margin-top:18px;width:40px;height:20px;",onLoad:function(){function a(a){a.on("mouseover",function(){this.addClass("cke_btn_over")},a);a.on("mouseout",function(){this.removeClass("cke_btn_over")},a)}var b=this.getDialog();f=p.getById(F);o=p.getById(G);f&&(b.addFocusable(f,
4+x),f.on("click",function(a){k();a.data&&a.data.preventDefault()},this.getDialog()),a(f));o&&(b.addFocusable(o,5+x),o.on("click",function(a){if(l){g.setValue(r);h.setValue(s)}else{g.setValue(m);h.setValue(n)}a.data&&a.data.preventDefault()},this),a(o))},setup:function(a){k(a.data.lock)},commit:function(a){a.setData("lock",e)},html:K}]},{type:"hbox",id:"alignment",requiredContent:v.align.requiredContent,children:[{id:"align",type:"radio",items:[[c.alignNone,"none"],[c.alignLeft,"left"],[c.alignCenter,
"center"],[c.alignRight,"right"]],label:c.align,setup:function(a){this.setValue(a.data.align)},commit:function(a){a.setData("align",this.getValue())}}]},{id:"hasCaption",type:"checkbox",label:b.captioned,requiredContent:v.caption.requiredContent,setup:function(a){this.setValue(a.data.hasCaption)},commit:function(a){a.setData("hasCaption",this.getValue())}}]},{id:"Upload",hidden:!0,filebrowser:"uploadButton",label:b.uploadTab,elements:[{type:"file",id:"upload",label:b.btnUpload,style:"height:40px"},
{type:"fileButton",id:"uploadButton",filebrowser:"info:src",label:b.btnUpload,"for":["Upload","upload"]}]}]}});