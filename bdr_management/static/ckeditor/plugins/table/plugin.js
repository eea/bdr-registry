﻿/*
 Copyright (c) 2003-2014, CKSource - Frederico Knabben. All rights reserved.
 For licensing, see LICENSE.md or http://ckeditor.com/license
*/
CKEDITOR.plugins.add("table",{requires:"dialog",lang:"af,ar,bg,bn,bs,ca,cs,cy,da,de,el,en,en-au,en-ca,en-gb,eo,es,et,eu,fa,fi,fo,fr,fr-ca,gl,gu,he,hi,hr,hu,id,is,it,ja,ka,km,ko,ku,lt,lv,mk,mn,ms,nb,nl,no,pl,pt,pt-br,ro,ru,si,sk,sl,sq,sr,sr-latn,sv,th,tr,tt,ug,uk,vi,zh,zh-cn",icons:"table",hidpi:!0,init:function(a){function d(a){return CKEDITOR.tools.extend(a||{},{contextSensitive:1,refresh:function(a,e){this.setState(e.contains("table",1)?CKEDITOR.TRISTATE_OFF:CKEDITOR.TRISTATE_DISABLED)}})}if(!a.blockless){var b=
a.lang.table;a.addCommand("table",new CKEDITOR.dialogCommand("table",{context:"table",allowedContent:"table{width,height}[align,border,cellpadding,cellspacing,summary];caption tbody thead tfoot;th td tr[scope];"+(a.plugins.dialogadvtab?"table"+a.plugins.dialogadvtab.allowedContent():""),requiredContent:"table",contentTransformations:[["table{width}: sizeToStyle","table[width]: sizeToAttribute"]]}));a.addCommand("tableProperties",new CKEDITOR.dialogCommand("tableProperties",d()));a.addCommand("tableDelete",
d({exec:function(a){var c=a.elementPath().contains("table",1);if(c){var b=c.getParent();1==b.getChildCount()&&!b.is("body","td","th")&&(c=b);a=a.createRange();a.moveToPosition(c,CKEDITOR.POSITION_BEFORE_START);c.remove();a.select()}}}));a.ui.addButton&&a.ui.addButton("Table",{label:b.toolbar,command:"table",toolbar:"insert,30"});CKEDITOR.dialog.add("table",this.path+"dialogs/table.js");CKEDITOR.dialog.add("tableProperties",this.path+"dialogs/table.js");a.addMenuItems&&a.addMenuItems({table:{label:b.menu,
command:"tableProperties",group:"table",order:5},tabledelete:{label:b.deleteTable,command:"tableDelete",group:"table",order:1}});a.on("doubleclick",function(a){a.data.element.is("table")&&(a.data.dialog="tableProperties")});a.contextMenu&&a.contextMenu.addListener(function(){return{tabledelete:CKEDITOR.TRISTATE_OFF,table:CKEDITOR.TRISTATE_OFF}})}}});