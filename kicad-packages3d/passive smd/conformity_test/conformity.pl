#!/usr/bin/perl

use strict;
use warnings;
use File::Basename;
use File::Find;
use File::Spec::Functions;
use Cwd qw();
use Getopt::Std;

my $recursive = 0;
my $backup = 1;
my %fg;

my $term = $ENV{'TERM'};
if (!defined($term) || ($term eq "")) {
  %fg = ( 'WT' => "", 'RD' => "", 'YL' => "", 'GR' => "", 'RS' => "" );
} else {
  %fg = ( 'WT' => "\033[1;37m", 'RD' => "\033[1;31m", 'YL' => "\033[1;33m",
          'GR' => "\033[1;32m", 'RS' => "\033[0;0m" );
}

sub VERSION_MESSAGE()
{
  print "\nKompas 3D STEP conformity fix script, version 0.1.\n";
}

sub HELP_MESSAGE()
{
  print "\nThis script makes Kompas 3D CAD system exported STEP\n";
  print "files fully conform to the ISO 10303-21 standard.\n";
  print "Usage: " . basename($0) . " [-cR] <dir|file> ...\n";
  print "  -c: don't backup files.\n";
  print "  -R: scan directories recursively.\n";
}

sub isdir
{
  my $path = $_[0];
  return -1 if ($path eq "");

  my $mode = (stat($path))[2] or return -1;

  return 1 if (($mode & 040000) == 040000);
  return 0;
}

sub process_file
{
  my $pathname = $_[0];
  return if (!defined($pathname) or $pathname eq "");
  my $outpn = "$pathname.fixed";

  print "processing " . $fg{'WT'} . $pathname . $fg{'RS'} . "...";
  open my $ifh, '<:encoding(UTF-8):raw', $pathname or do {print $fg{'RD'} . "$!" . $fg{'RS'} . "\n"; return 1};
  open my $ofh, '>:encoding(UTF-8):raw', $outpn or do {print $fg{'RD'} . "$!" . $fg{'RS'} . "\n"; return 1};

  my $alldone = 0;
  my $ascon1_3 = 0;
  while (my $line = <$ifh>) {
    if ($alldone < 3) {
      if ($line =~ m/\QASCON STEP Converter 1.3\E/) {
        $ascon1_3 = 1;
      }
      if (($alldone & 1) == 0) {
        if ($line =~ m/^(?<pre>\W*#[0-9]+\W*=\W*\()(?<post>\W*NAMED_UNIT\W*(\W*\$\W*)\W*MASS_UNIT\W*(\W*)\W*SI_UNIT\W*\(\W*\$\W*,\W*\.GRAM\..*)$/) {
          if ($ascon1_3) {
            chomp $line;
            $line = "$+{pre}DERIVED_UNIT_ELEMENT(\$,-1.)$+{post}\n";
          }
          $alldone |= 1;
        }
      }
      if (($alldone & 2) == 0) {
        if ($line =~ m/^(?<pre>\W*#[0-9]+\W*=\W*)MECHANICAL_CONTEXT(?<post>.*)$/) {
          if ($ascon1_3) {
            chomp $line;
            $line = "$+{pre}PRODUCT_CONTEXT$+{post}\n";
          }
          $alldone |= 2;
        }
      }
    }
    print { $ofh } $line or do {print $fg{'RD'} . "$!" . $fg{'RS'} . "\n"; return 1};
  }
  close $ofh;
  close $ifh;

  if ($alldone) {
    if ($backup) {
      rename $pathname, "$pathname.bak" or do {print $fg{'RD'} . "$!" . $fg{'RS'} . "\n"; return 1};
    }
    rename $outpn, "$pathname" or do {print $fg{'RD'} . "$!" . $fg{'RS'} . "\n"; return 1};
    print $fg{'GR'} . "Fixed" . $fg{'RS'} . "\n";
  } else {
    unlink $outpn or do {print $fg{'RD'} . "$!" . $fg{'RS'} . "\n"; return 0; }; # the job is done anyway
    print $fg{'RS'} . "Skipped" . $fg{'RS'} . "\n";
  }

  return 0;
}

sub find_cb()
{
  my $pathname = $File::Find::name;
  return if (-d $pathname);
  my($filename, $dirs, $suffix) = fileparse($pathname, (qr/\Q.stp\E/i, qr/\Q.step\E/i));
  return if ($suffix eq "");

  process_file($pathname);
}

sub process_args
{
  my @args = @_;
  push @args, Cwd::abs_path() if ($#args < 0);

  if ($recursive) {
    find( { wanted => \&find_cb, no_chdir => 1} , @args);
  } else {
	foreach my $arg (@args) {
      my $bdir = isdir($arg);
      if ($bdir == 1) {
        opendir(DIR, $arg) or die $!;
        while (my $name = readdir(DIR)) {
          my $pathname = catfile($arg, $name);
          next if (-d $pathname);
          my($filename, $dirs, $suffix) = fileparse($pathname, (qr/\Q.stp\E/i, qr/\Q.step\E/i));
          next if ($suffix eq "");

          process_file($pathname);
        }
        closedir(DIR);
      } elsif ($bdir == 0) {
        process_file($arg);
      } else {
        warn "can't stat $arg: $!\n";
      }
    }
  }

  return;
}

$Getopt::Std::STANDARD_HELP_VERSION = "true";
my %options;
getopts("cR",\%options);
if (defined $options{R}) {
  $recursive = 1;
}
if (defined $options{c}) {
  $backup = 0;
}
if ($#ARGV < 0) {
  HELP_MESSAGE;
  exit(1);
}

process_args(@ARGV);
