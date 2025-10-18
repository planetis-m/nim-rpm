Name:           nimony-devel
Version:        0.1.0
Release:        1%{?dist}
Summary:        Nimony compiler and toolchain (development version)

License:        MIT
URL:            https://github.com/nim-lang/nimony
Source0:        https://github.com/nim-lang/nimony/archive/refs/heads/master.tar.gz#/nimony-master-%{version}.tar.gz

BuildRequires:  nim
BuildRequires:  gcc
BuildRequires:  git

Requires:       gcc

# Disable debuginfo package since Nim binaries don't have standard debug symbols
%global debug_package %{nil}

%description
Nimony is a new Nim implementation that is in heavy development.

%prep
%autosetup -n nimony-master

# Initialize git repo for hastur build script
git init
git config user.email "build@copr"
git config user.name "COPR Build"
git add .
git commit -m "Initial commit for build"

# Fetch git submodules manually since we're building from tarball
# The hastur script expects git submodules to be present
git submodule init || true

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
install -Dm 755 bin/* -t %{buildroot}%{_libdir}/nimony/bin

# Create symlinks in /usr/bin
ln -sf ../%{_lib}/nimony/bin/hexer   %{buildroot}%{_bindir}/hexer
ln -sf ../%{_lib}/nimony/bin/nifc    %{buildroot}%{_bindir}/nifc
ln -sf ../%{_lib}/nimony/bin/nifler  %{buildroot}%{_bindir}/nifler
ln -sf ../%{_lib}/nimony/bin/nifmake %{buildroot}%{_bindir}/nifmake
ln -sf ../%{_lib}/nimony/bin/nimony  %{buildroot}%{_bindir}/nimony
ln -sf ../%{_lib}/nimony/bin/nimsem  %{buildroot}%{_bindir}/nimsem

# Install components
cp -R lib %{buildroot}%{_libdir}/nimony/
cp -R vendor %{buildroot}%{_libdir}/nimony/
cp -R tools %{buildroot}%{_libdir}/nimony/
cp -R doc %{buildroot}%{_datadir}/nimony/

%files
%license license.txt
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
* Sat Jan 18 2025 planetis-m <planetis@example.com> - 0.1.0-1
- Initial package build from git master branch
- Added nim build dependency from COPR
