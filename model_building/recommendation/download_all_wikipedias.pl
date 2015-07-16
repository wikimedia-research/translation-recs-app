#!/usr/bin/perl

my $links_to_langs = `wget -q -O - 'http://dumps.wikimedia.org/backup-index.html' | grep '<a href=".*wiki/[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]">'`;

foreach my $line (split /\n/, $links_to_langs) {
  if ($line =~ m{<a href="(.*wiki/\d{8})">.*wiki</a>}) {
    my $path = $1;
    download($path);
  }
}


sub download {
  my $path = shift;
  my $html = `wget -q -O - 'http://dumps.wikimedia.org/$path'`;
  print "Attempting to get $path\n";
  # Dump complete.
  if ($html =~ m{<span class='done'>Dump complete</span>}) {
    print "  Dump complete: $path\n";
    if ($html =~ m{<li class='file'><a href="/(.*/(.*-pages-articles-multistream\.xml)\.bz2)">.*-pages-articles-multistream\.xml\.bz2</a>.*</li>}) {
      my $bz2_full_path = $1;
      my $inflated_file = $2;
      print "  Downloading $1\n";
      `wget -O - 'http://dumps.wikimedia.org/$bz2_full_path' | bunzip2 | hadoop fs -put - /user/west1/wikipedia_dumps/$inflated_file`;
    }
  }
  # Dump in progress.
  elsif ($html =~ m{This dump is in progress; see also the <a href="(../\d{8})/">previous dump from .*</a>}) {
    print "  Dump in progress: $path\n";
    download("$path/$1");
  }
  # Error.
  else {
    print "  Don't know what to do with $path\n";
  }
}
