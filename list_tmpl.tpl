% rebase('base.tpl')
<div class="alert alert-success" role="alert"><b>KCPS東日本 インスタンス一覧</b></div>
<table class="table table-striped">
    <tr>
        <td><b>作成日</b></td>
        <td><b>インスタンス名</b></td>
        <td><b>作成から経過日</b></td>
        <td><b>状態</b></td>
    </tr>
%for i in range(len(api_dic["created"])):
    <tr>
        <td>{{api_dic["created"][i]}}</td>
        <td>{{api_dic["displayname"][i]}}</td>
        <td>{{api_dic["date_delta"][i]}}</td>
        %if api_dic["state"][i] == "Stopped":
            <td><b><font color="red">{{api_dic["state"][i]}}</font></b></td>
        %elif api_dic["state"][i] == "Running":
            <td><b><font color="green">{{api_dic["state"][i]}}</font></b></td>
        %else:
            <td>{{api_dic["state"][i]}}</td>
        %end
    </tr>
%end
</table>
<div class="alert alert-success" role="alert"><b>KCPS東日本 ファイアウォールルール一覧</b></div>
<table class="table table-striped">
    <tr>
        <td><b>グローバルIPアドレス</b></td>
        <td><b>許可元IPアドレス</b></td>
        <td><b>許可ポート</b></td>
    </tr>
%for i in range(len(fw_dic["ipaddress"])):
    <tr>
        <td>{{fw_dic["ipaddress"][i]}}</td>
        %if fw_dic["cidrlist"][i] == "0.0.0.0/0":
            <td><blink><b><font color="red">{{fw_dic["cidrlist"][i]}}</font></b></blink></td>
        %else:
            <td>{{fw_dic["cidrlist"][i]}}</td>
        %end
        <td>{{fw_dic["protocol_rangeport"][i]}}</td>
    </tr>
%end
</table>
