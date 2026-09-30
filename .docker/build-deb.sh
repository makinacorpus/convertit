#!/usr/bin/env bash
set -euo pipefail

# Workdir safe for git if running as root
git config --global --add safe.directory /workspace 2>/dev/null || true

TARGET_DIR="/opt/convertit"
PKG_ROOT="/tmp/pkg-dist"
PYTHON_VERSION="${PYTHON_VERSION:-3.14}"

# Détermination robuste de la version du paquet Debian
VERSION=""

# 1. Depuis DEB_VERSION ou VERSION (passé en build-arg / env)
if [ -n "${DEB_VERSION:-}" ] && [ "${DEB_VERSION}" != "unknown" ]; then
    VERSION="${DEB_VERSION}"
elif [ -n "${VERSION:-}" ] && [ "${VERSION}" != "unknown" ]; then
    VERSION="${VERSION}"
fi

# 2. Depuis le fichier convertit/VERSION
if [ -z "${VERSION}" ] && [ -f convertit/VERSION ]; then
    FILE_VER="$(tr -d '[:space:]' < convertit/VERSION 2>/dev/null || true)"
    if [ -n "${FILE_VER}" ] && [ "${FILE_VER}" != "unknown" ]; then
        VERSION="${FILE_VER}"
    fi
fi

# 3. Depuis dpkg-parsechangelog si valide
if [ -z "${VERSION}" ] && [ -f debian/changelog ]; then
    CL_VER="$(dpkg-parsechangelog -S Version 2>/dev/null || true)"
    if [ -n "${CL_VER}" ] && [ "${CL_VER}" != "unknown" ]; then
        VERSION="${CL_VER}"
    fi
fi

# 4. Extraction directe depuis la première ligne de debian/changelog
if [ -z "${VERSION}" ] && [ -f debian/changelog ]; then
    HEADER_VER="$(sed -n '1s/^[a-zA-Z0-9_-]\+ *(\([^)]*\)).*/\1/p' debian/changelog 2>/dev/null || true)"
    if [ -n "${HEADER_VER}" ] && [ "${HEADER_VER}" != "unknown" ]; then
        VERSION="${HEADER_VER}"
    fi
fi

# 5. Valeur de secours par défaut
if [ -z "${VERSION}" ]; then
    VERSION="2.2.6"
fi

# Nettoyage de la version (suppression des espaces et du préfixe 'v')
VERSION="$(echo "${VERSION}" | tr -d '[:space:]' | sed 's/^v//')"

# Validation : doit commencer par un chiffre pour être accepté par dpkg
if ! echo "${VERSION}" | grep -q '^[0-9]'; then
    echo "AVERTISSEMENT: La version '${VERSION}' ne commence pas par un chiffre, repli sur '2.2.6'" >&2
    VERSION="2.2.6"
fi

# Nettoyage et vérification de la validité de debian/changelog
if [ -f debian/changelog ]; then
    if grep -q "UNRELEASED" debian/changelog 2>/dev/null; then
        sed -i -re "1s/\) UNRELEASED;/\) stable;/" debian/changelog
    fi
    CL_TEST="$(dpkg-parsechangelog -S Version 2>/dev/null || true)"
    if [ -z "${CL_TEST}" ] || [ "${CL_TEST}" = "unknown" ]; then
        sed -i "1s/^[a-zA-Z0-9_-]\+ *([^)]*) *[^;]*;/convertit (${VERSION}) stable;/" debian/changelog 2>/dev/null || true
    fi
fi

echo "=== Version Debian retenue : ${VERSION} ==="

echo "=== 1. Résolution et installation des dépendances de build (mk-build-deps) ==="
apt-get update -qq

mk-build-deps --install --remove \
    --tool='apt-get -o Debug::pkgProblemResolver=yes --no-install-recommends -y' \
    debian/control || true

rm -f convertit-build-deps_*

echo "=== 2. Préparation du runtime Python ${PYTHON_VERSION} via uv ==="
rm -rf "${TARGET_DIR}" "${PKG_ROOT}"
mkdir -p "${TARGET_DIR}/runtime" "${PKG_ROOT}"

export UV_PYTHON_INSTALL_DIR="${TARGET_DIR}/runtime"
uv python install "${PYTHON_VERSION}" --install-dir "${UV_PYTHON_INSTALL_DIR}"

PYTHON_BIN=$(find "${UV_PYTHON_INSTALL_DIR}" -name python3 -perm -111 | head -n 1)
if [ -z "${PYTHON_BIN}" ]; then
    echo "ERREUR : Binaire python3 introuvable dans ${UV_PYTHON_INSTALL_DIR}" >&2
    exit 1
fi
echo "Interpréteur Python utilisé : ${PYTHON_BIN}"

echo "=== 3. Création du venv et installation des dépendances ==="
uv venv "${TARGET_DIR}" --allow-existing --python "${PYTHON_BIN}"
ln -sfn . "${TARGET_DIR}/venv"

echo "Installation des dépendances..."
uv pip install --python "${TARGET_DIR}/bin/python" "setuptools<81" wheel
uv pip install -r requirements.txt --python "${TARGET_DIR}/bin/python"
uv pip install --no-deps . --python "${TARGET_DIR}/bin/python"

echo "=== 4. Optimisation de l'arborescence ==="
find "${TARGET_DIR}/runtime" -type d -name "test" -prune -exec rm -rf {} + 2>/dev/null || true
find "${TARGET_DIR}/runtime" -type d -name "tests" -prune -exec rm -rf {} + 2>/dev/null || true
find "${TARGET_DIR}" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "${TARGET_DIR}" -type f -name "*.pyc" -delete 2>/dev/null || true

echo "=== 5. Préparation de l'arborescence du paquet (staging) ==="
mkdir -p "${PKG_ROOT}/opt" \
         "${PKG_ROOT}/DEBIAN" \
         "${PKG_ROOT}/lib/systemd/system"

# Fichier de configuration
cp production.ini "${TARGET_DIR}/convertit.ini"

# Copie de l'arborescence /opt/convertit
cp -a "${TARGET_DIR}" "${PKG_ROOT}/opt/"

# Fichiers systemd
cp debian/convertit.service "${PKG_ROOT}/lib/systemd/system/"
chmod 644 "${PKG_ROOT}/lib/systemd/system/convertit.service"

# Fichiers de contrôle DEBIAN
# conffiles
if [ -f debian/conffiles ]; then
    cp debian/conffiles "${PKG_ROOT}/DEBIAN/conffiles"
    chmod 644 "${PKG_ROOT}/DEBIAN/conffiles"
fi

# Scripts postinst, prerm, postrm avec intégration systemd
sed '/#DEBHELPER#/d' debian/postinst > "${PKG_ROOT}/DEBIAN/postinst"
cat << 'EOF' >> "${PKG_ROOT}/DEBIAN/postinst"

# Intégration systemd
if [ "$1" = "configure" ] || [ "$1" = "abort-upgrade" ] || [ "$1" = "abort-deconfigure" ] || [ "$1" = "abort-remove" ] ; then
	if which deb-systemd-helper >/dev/null 2>&1; then
		deb-systemd-helper enable 'convertit.service' >/dev/null 2>&1 || true
	fi
	if [ -d /run/systemd/system ]; then
		systemctl --system daemon-reload >/dev/null 2>&1 || true
		systemctl restart convertit.service >/dev/null 2>&1 || true
	fi
fi
EOF
chmod 755 "${PKG_ROOT}/DEBIAN/postinst"

cat << 'EOF' > "${PKG_ROOT}/DEBIAN/prerm"
#!/bin/sh -e
if [ "$1" = "remove" ] || [ "$1" = "upgrade" ] || [ "$1" = "deconfigure" ]; then
	if [ -d /run/systemd/system ]; then
		systemctl stop convertit.service >/dev/null 2>&1 || true
	fi
fi
exit 0
EOF
chmod 755 "${PKG_ROOT}/DEBIAN/prerm"

sed '/#DEBHELPER#/d' debian/postrm > "${PKG_ROOT}/DEBIAN/postrm"
cat << 'EOF' >> "${PKG_ROOT}/DEBIAN/postrm"

if [ "$1" = "purge" ]; then
	rm -rf /var/cache/convertit || true
	deluser --quiet convertit || true
	if which deb-systemd-helper >/dev/null 2>&1; then
		deb-systemd-helper purge 'convertit.service' >/dev/null 2>&1 || true
	fi
fi
if [ -d /run/systemd/system ]; then
	systemctl --system daemon-reload >/dev/null 2>&1 || true
fi
exit 0
EOF
chmod 755 "${PKG_ROOT}/DEBIAN/postrm"

# DEBIAN/control binaire
INSTALLED_SIZE=$(du -sk "${PKG_ROOT}" | awk '{print $1}')
DEPENDS=$(awk '
    /^Package:/ { in_pkg=1 }
    in_pkg && /^Depends:/ { in_dep=1; next }
    in_dep && /^[A-Za-z0-9_-]*:/ { in_dep=0; in_pkg=0 }
    in_dep { print }
' debian/control | tr -d '\n' | sed -e 's/\${[^}]*},*//g' -e 's/^[ ,]*//' -e 's/[ ,]*$//' -e 's/  */ /g' -e 's/, *,/, /g')

cat << EOF > "${PKG_ROOT}/DEBIAN/control"
Package: convertit
Version: ${VERSION}
Architecture: amd64
Maintainer: Makina Corpus <geobi@makina-corpus.com>
Installed-Size: ${INSTALLED_SIZE}
Depends: ${DEPENDS}
Section: python
Priority: optional
Homepage: https://github.com/makinacorpus/convertit
Description: A file conversion Web API in Pyramid
 Convertit is a format conversion webservice.
 .
 Retrieve your document in an other format ! The input file is converted and served back !
 Using a dead simple GET request, documents are pulled. Using POST request, it takes the attachment.
 .
 Supported conversions:
 .
 - odt -> pdf
 - odt -> doc
 - ods -> xls
 - csv -> ods
 - csv -> xls
 - svg -> pdf
 - svg -> png
 .
 Previously converted documents are cleaned along the way (on each request).
EOF
chmod 644 "${PKG_ROOT}/DEBIAN/control"

echo "=== 6. Construction du paquet .deb ==="
mkdir -p /dpkg
DEB_FILE="/dpkg/convertit_${VERSION}_amd64.deb"
dpkg-deb -Zxz --build --root-owner-group "${PKG_ROOT}" "${DEB_FILE}"

echo "=== Inspection du paquet généré ==="
dpkg-deb -I "${DEB_FILE}"

# Nettoyage
rm -rf "${PKG_ROOT}"

echo "=== Succès : ${DEB_FILE} généré avec succès ==="
