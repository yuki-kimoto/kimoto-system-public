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
my $mail_send_only = 'send@kimoto-system.co.jp';

# 木本システムカスタマーセンター
my $mail_kimoto_sysmte_customer_center = 'support@kimoto-system.co.jp';

# Errors
my @errors;

# 会社名
my $company_name = $q->param('company_name');
$company_name = decode('UTF-8', $company_name);
unless (length $company_name) {
  push @errors, "会社名 (個人事業主様の場合は屋号)を入力してください。";
}

# 担当者様名
my $staff_name = $q->param('staff_name');
$staff_name = decode('UTF-8', $staff_name);
unless (length $staff_name) {
  push @errors, "担当者様名 (個人事業主様の場合は氏名)を入力してください。";
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

# サービス
my $service = $q->param('service');
$service = decode('UTF-8', $service);

unless ($service) {
  push @errors, "サービス・基本価格を選択してください。";
}

# 開発期間
my $period = $q->param('period');
$period = decode('UTF-8', $period);

unless ($period > 0) {
  push @errors, "開発期間を選択してください。";
}

# 業種
my $industry = $q->param('industry');
$industry = decode('UTF-8', $industry);

unless ($industry) {
  push @errors, "業種を選択してください。";
}

# 実現したいWebシステムの内容を記入
my $message = $q->param('message');
$message = decode('UTF-8', $message);
unless (length $message) {
  push @errors, "実現したいWebシステムの内容を入力してください。";
}

# Response
my $res = <<"EOS";
Content-type: application/json;

EOS

my $res_data = {};

unless (@errors) {

  # Mail title
  my $subject = "【見積もり】${company_name} ${staff_name}様";

  # Mail body
  my $mail_body = <<"EOS";
会社名: $company_name
担当者様名: $staff_name
メールアドレス: $email
電話番号: $tel
サービス: $service
開発期間: ${period}ヵ月
業種: $industry
実現したいWebシステムの内容を記入:

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
  my $subject = 'お見積り内容 - Perl Webシステム開発の木本システム株式会社';
  my $mail_body = <<"EOS";
お見積りを以下の内容で受け付けました。

会社名: $company_name
担当者様名: $staff_name
メールアドレス: $email
電話番号: $tel
サービス: $service
開発期間: ${period}ヵ月
業種: $industry
実現したいWebシステムの内容を記入:

$message

この内容は自動返信メールによるものです。

内容を確認後、ご連絡差し上げます。

------------------------------------------------------------
木本システム株式会社

https://kimoto-system.co.jp/

〒105-0012 東京都港区芝大門一丁目２番２３号 旭ビル３F

カスタマーセンター

support\@kimoto-system.co.jp

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
