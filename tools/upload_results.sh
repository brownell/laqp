#!/bin/bash
# Upload result files (db, final_reports) to Fly.io

curl -s https://laqp.fly.dev/health > /dev/null
sleep 3 
flyctl ssh console << EOF
sleep 3
exit
EOF

echo "should be back at local prompt"

echo "============================="
echo "📦 DELETING all remote files: DB, final reports, temp files"
flyctl ssh console << EOF
rm -rf /data/final_reports/*
rm -rf /data/db/*
rm -rf /app/temp/*
exit
EOF
read -rsp $'DELETED all remote files.....Press any key to continue...\n' -n1

echo "============================="
echo "📦 Creating archive... for final reports"
tar -czf temp/final_reports.tar.gz -C ../laqp_data/final_reports .
read -rsp $'Created reports tar.....Press any key to continue...\n' -n1

echo "============================="
echo "📤 Uploading to Fly.io... for final reports"
flyctl ssh sftp shell << EOF
put temp/final_reports.tar.gz /app/temp/final_reports.tar.gz
cd /app/temp
ls
EOF
read -rsp $'Uploaded reports tar.....Press any key to continue...\n' -n1

echo "============================="
echo "Extracting reports tar"
flyctl ssh console << EOF
echo "📂 Extracting on Fly.io... final reports"
cd /data/final_reports
ls
tar -xzf /app/temp/final_reports.tar.gz
rm /app/temp/final_reports.tar.gz
echo "✅ Extracted files:"
ls
exit
EOF
read -rsp $'Extracted reports tar on fly.io.....Press any key to continue...\n' -n1

echo "============================="
echo "📦 Creating archive... for db"
tar -czf temp/db.tar.gz -C ../laqp_data/database .
read -rsp $'Created DB tar.....Press any key to continue...\n' -n1


echo "============================="
echo "📤 Uploading to Fly.io... for db"
flyctl ssh sftp shell << EOF
put temp/db.tar.gz /app/temp/db.tar.gz
cd /app/temp
ls
EOF
read -rsp $'Uploaded DB tar....Press any key to continue...\n' -n1

echo "============================="
echo "📂 Extracting on Fly.io... db"
flyctl ssh console << EOF
cd /data/db
tar -xzf /app/temp/db.tar.gz
rm /app/temp/db.tar.gz
echo "✅ Extracted files:"
ls
exit
EOF
read -rsp $'Extracted DB tar on fly.io.....Press any key to continue...\n' -n1

echo "============================="
echo "🧹 Cleaning up local archive..."
rm temp/final_reports.tar.gz
rm temp/db.tar.gz
echo "✅ Upload complete! **********"
