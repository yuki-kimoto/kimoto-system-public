#!/usr/bin/env perl

use strict;
use warnings;
use utf8;

use CGI;
use JSON::PP 'encode_json';
use MIME::Lite;

use Encode 'decode', 'encode';

my $q = CGI->new;

# 送信専用メール
my $mail_send_only = 'send@perlri.com';

# Perl総合研究所カスタマーセンター
my $mail_kimoto_sysmte_customer_center = 'support@perlri.com';

# Errors
my @errors;

# 担当者様名
my $staff_name = $q->param('staff_name');
$staff_name = decode('UTF-8', $staff_name);
unless (length $staff_name) {
  push @errors, "担当者様名を入力してください。";
}

# メールアドレス
my $email = $q->param('email');
$email = decode('UTF-8', $email);

unless (length $email && $email =~ /\@/) {
  push @errors, "正しいEメールアドレスを入力してください。";
}

# 電話番号
my $tel = $q->param('tel');
$tel = decode('UTF-8', $tel);

unless (length $tel) {
  push @errors, "電話番号を入力してください。";
}

# 実現したいWebシステムの内容を記入
my $message = $q->param('message');
$message = decode('UTF-8', $message);
unless (length $message) {
  push @errors, "お問い合わせ内容を入力してください。";
}

# Response
my $res = <<"EOS";
Content-type: application/json;

EOS

my $res_data = {};

unless (@errors) {

  # Mail title
  my $subject = "【お問い合わせ】${staff_name}様";

  # Mail body
  my $mail_body = <<"EOS";
担当者様名: $staff_name
メールアドレス: $email
電話番号: $tel
お問い合わせ内容

$message
EOS

  # Send mail
  my $msg = MIME::Lite->new(
    From    => $mail_send_only,
    To      => $mail_kimoto_sysmte_customer_center,
    Subject => encode('MIME-Header', $subject),
    Type    => 'multipart/mixed'
  );
  $msg->attach(
    Type     => 'TEXT',
    Data     => encode('UTF-8', $mail_body),
  );
  unless ($msg->send) {
    push @errors, "メールの送信に失敗しました。";
  }
}

if (@errors) {
  $res_data->{success} = 0;
  $res_data->{errors} = \@errors;
}
else {
  $res_data->{success} = 1;
  
  # 自動返信メール
  my $subject = 'お問い合わせ内容 - 株式会社Perl総合研究所';
  my $mail_body = <<"EOS";
お問い合わせを以下の内容で受け付けました。

担当者様名: $staff_name
メールアドレス: $email
電話番号: $tel
お問い合わせ内容:

$message

この内容は自動返信メールによるものです。

内容を確認後、ご連絡差し上げます。

------------------------------------------------------------
株式会社Perl総合研究所

http://www.perlri.com/

〒105-0012 東京都港区芝大門一丁目２番２３号 旭ビル３F

カスタマーセンター

support\@perlri.com

03-6435-7439

営業時間10:00～19:00（月～金営業、祝日・年末年始休み)
EOS

  # Send mail
  my $msg = MIME::Lite->new(
    From    => $mail_send_only,
    To      => $email,
    Subject => encode('MIME-Header', $subject),
    Type    => 'multipart/mixed'
  );
  $msg->attach(
    Type     => 'TEXT',
    Data     => encode('UTF-8', $mail_body),
  );
  $msg->send;
}

# JSON response
my $res_json = encode_json($res_data);
$res .= "$res_json\n";

# Print response
print $res;
