%global debug_package %{nil}
%global _build_id_links none

%define date %(date +%Y%m%d)

Name:           nimony-git
Version:        0.2.0~devel.%{date}
Release:        %autorelease
Summary:        Nimony compiler and toolchain (development version)

License:        MIT
URL:            https://github.com/nim-lang/nimony
Source0:        https://github.com/nim-lang/nimony/archive/refs/heads/master.tar.gz#/nimony-master-%{version}.tar.gz
Source1:        https://github.com/nim-lang/mimalloc/archive/refs/heads/master.tar.gz#/mimalloc-master.tar.gz
Source2:        https://github.com/nim-lang/errorcodes/archive/refs/heads/master.tar.gz#/errorcodes-master.tar.gz

BuildRequires:  nim
BuildRequires:  gcc
BuildRequires:  git

Requires:       gcc
Provides:       nimony = %{version}-%{release}
Conflicts:      nimony

%description
Nimony is a new Nim implementation that is in heavy development.

%prep
%autosetup -n nimony-master
# Extract submodules manually
tar -xzf %{SOURCE1} -C vendor/mimalloc --strip-components=1
tar -xzf %{SOURCE2} -C vendor/errorcodes --strip-components=1

# Initialize git repo for hastur build script
git init
git config user.email "build@copr"
git config user.name "COPR Build"
git add .
git commit -m "Initial commit for build"
# The hastur script expects git submodules to be present
git submodule init || true

%build
# Build all components using hastur
nim c -r src/hastur build all --release
nim c -r src/hastur build validator --release

%install
# Create directory structure
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_libdir}/nimony
mkdir -p %{buildroot}%{_libdir}/nimony/bin
mkdir -p %{buildroot}%{_datadir}/nimony

# Install binaries to /usr/lib/nimony/bin
install -Dm 755 bin/* -t %{buildroot}%{_libdir}/nimony/bin

# Create symlinks in /usr/bin
ln -sf ../%{_lib}/nimony/bin/nimony  %{buildroot}%{_bindir}/nimony
ln -sf ../%{_lib}/nimony/bin/dagon  %{buildroot}%{_bindir}/dagon
ln -sf ../%{_lib}/nimony/bin/nimpac  %{buildroot}%{_bindir}/nimpac

# Install components
cp -R lib %{buildroot}%{_libdir}/nimony/
cp -R tools %{buildroot}%{_libdir}/nimony/
cp -R doc %{buildroot}%{_datadir}/nimony/

# Install compiler plugins
mkdir -p %{buildroot}%{_libdir}/nimony/src
cp -R src/lib %{buildroot}%{_libdir}/nimony/src
cp -R src/models %{buildroot}%{_libdir}/nimony/src
mkdir -p %{buildroot}%{_libdir}/nimony/src/nimony
cp src/nimony/nimony_model.nim %{buildroot}%{_libdir}/nimony/src/nimony/
cp -R src/nimony/lib %{buildroot}%{_libdir}/nimony/src/nimony

# Install vendor - only copy what's needed
mkdir -p %{buildroot}%{_libdir}/nimony/vendor/mimalloc
mkdir -p %{buildroot}%{_libdir}/nimony/vendor/errorcodes

cp -R vendor/mimalloc/src %{buildroot}%{_libdir}/nimony/vendor/mimalloc/
cp -R vendor/mimalloc/include %{buildroot}%{_libdir}/nimony/vendor/mimalloc/
cp vendor/mimalloc/LICENSE %{buildroot}%{_libdir}/nimony/vendor/mimalloc/

cp -R vendor/errorcodes/src %{buildroot}%{_libdir}/nimony/vendor/errorcodes/
cp vendor/errorcodes/LICENSE %{buildroot}%{_libdir}/nimony/vendor/errorcodes/

%files
%license license.txt
%doc README.md
%{_bindir}/nimony
%{_bindir}/dagon
%{_bindir}/nimpac
%{_libdir}/nimony
%{_datadir}/nimony

%changelog
%autochangelog
