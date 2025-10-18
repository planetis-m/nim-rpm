Name:           nimony
Version:        0.1.0
Release:        1%{?dist}
Summary:        Nimony compiler and toolchain

License:        MIT
URL:            https://github.com/nim-lang/nimony
Source0:        https://github.com/nim-lang/nimony/archive/refs/heads/devel.tar.gz

BuildRequires:  nim
BuildRequires:  gcc
BuildRequires:  git

Requires:       gcc

%description
Nimony is a modern compiler and toolchain for the Nim programming language.
It includes various tools like nifc, nifler, nifmake, and others for
working with NIF (Nim Intermediate Format) files.

%prep
%setup -q -n nimony-devel

%build
# Build all components using hastur
nim c -r src/hastur build all

%install
# Create directory structure
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_libdir}/nimony
mkdir -p %{buildroot}%{_libdir}/nimony/bin
mkdir -p %{buildroot}%{_datadir}/nimony

# Install binaries to /usr/lib/nimony/bin
install -Dm 755 nimony/bin/* -t %{buildroot}%{_libdir}/nimony/bin

# Create symlinks in /usr/bin
ln -sf %{_libdir}/nimony/bin/hexer   %{buildroot}%{_bindir}/hexer
ln -sf %{_libdir}/nimony/bin/nifc    %{buildroot}%{_bindir}/nifc
ln -sf %{_libdir}/nimony/bin/nifler  %{buildroot}%{_bindir}/nifler
ln -sf %{_libdir}/nimony/bin/nifmake %{buildroot}%{_bindir}/nifmake
ln -sf %{_libdir}/nimony/bin/nimony  %{buildroot}%{_bindir}/nimony
ln -sf %{_libdir}/nimony/bin/nimsem  %{buildroot}%{_bindir}/nimsem

# Install components
cp -R nimony/lib %{buildroot}%{_libdir}/nimony/
cp -R nimony/vendor %{buildroot}%{_libdir}/nimony/
cp -R nimony/tools %{buildroot}%{_libdir}/nimony/
cp -R nimony/doc %{buildroot}%{_datadir}/nimony/

%files
%license LICENSE
%doc README.md
%{_bindir}/hexer
%{_bindir}/nifc
%{_bindir}/nifler
%{_bindir}/nifmake
%{_bindir}/nimony
%{_bindir}/nimsem
%{_libdir}/nimony
%{_datadir}/nimony

%changelog
* Sat Oct 18 2025 planetis-m <planetis@example.com> - 0.1.0-1
- Initial package build from git
- Added nim build dependency from COPR
