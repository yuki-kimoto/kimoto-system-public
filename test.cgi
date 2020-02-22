#!/usr/bin/env perl

use strict;
use warnings;
use Encode 'encode';

# Response
my $res = <<"EOS";
Content-type: application/json;

1
EOS
print encode('UTF-8', $res);
