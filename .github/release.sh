#!/bin/sh
I3WND=i3-workspace-names-daemon
cd /home/runner/work/$I3WND

newest_deb=$(ls -t *.deb | head -n 1)
md5sum "$newest_deb" > "${newest_deb}.md5"

PV=`grep -e 'version' "$I3WND/setup.py" | cut -d "'" -f 2`
    if [ "v$PV" != $GITHUB_REF_NAME ] ; then
    echo "Version mismatch 'v$PV' != '$GITHUB_REF_NAME'";
    exit 1;
fi

# create the release as draft and grab the id
RELEASE_ID=`curl -L \
    -X POST \
    -H "Accept: application/vnd.github+json" \
    -H "Authorization: Bearer ${GH_TOKEN}" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    https://api.github.com/repos/$I3WND/$I3WND/releases \
    -d "{\"tag_name\":\"v${PV}\",\"target_commitish\":\"master\",\"name\":\"v${PV}\",\"body\":\"Release ${PV}\",\"draft\":true,\"prerelease\":false,\"generate_release_notes\":false}"\
    -s \
| python -c "import json; from sys import stdin; print(json.loads(stdin.read())['id'])"`

echo "Created Release with ID $RELEASE_ID"

if [[ -z $RELEASE_ID || ${#RELEASE_ID} -gt 18 ]] ; then
    echo "sorry, it didn't work..."
    exit 2
fi

# upload deb
curl -L \
-X POST \
-H "Accept: application/vnd.github+json" \
-H "Authorization: Bearer ${GH_TOKEN}" \
-H "X-GitHub-Api-Version: 2022-11-28" \
-H "Content-Type: application/octet-stream" \
"https://uploads.github.com/repos/$I3WND/$I3WND/releases/${RELEASE_ID}/assets?name=${newest_deb}" \
--data-binary "@${newest_deb}" 2>&1 >/dev/null

# upload md5 checksum
curl -L \
-X POST \
-H "Accept: application/vnd.github+json" \
-H "Authorization: Bearer ${GH_TOKEN}" \
-H "X-GitHub-Api-Version: 2022-11-28" \
-H "Content-Type: application/octet-stream" \
"https://uploads.github.com/repos/$I3WND/$I3WND/releases/${RELEASE_ID}/assets?name=${newest_deb}.md5" \
--data-binary "@${newest_deb}.md5" 2>&1 >/dev/null
