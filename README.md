# Security Camera Plugin for Dispatcharr

Add RTSP, HTTP, and MJPEG security camera feeds as channels in Dispatcharr.

## Features

- ✅ Add any RTSP/HTTP/MJPEG camera stream as a channel
- ✅ Organize cameras into channel groups
- ✅ Set custom channel numbers
- ✅ Optional logo/icon support for streams
- ✅ Update existing camera channels
- ✅ List all security camera channels
- ✅ Easy camera channel deletion

## Installation

1. Upload the Zip file through Dispatcharr plugins
2. Restart Dispatcharr container
3. The plugin will appear in your plugins list as "Security Camera"

## Usage

### Creating a Camera Channel

1. Navigate to the Security Camera plugin
2. Fill in the required fields:
   - **Camera Stream URL**: Your camera's RTSP/HTTP/MJPEG URL
     - Example RTSP: `rtsp://username:password@192.168.1.100:554/stream1`
     - Example HTTP: `http://192.168.1.100:8080/video`
     - Example MJPEG: `http://192.168.1.100/mjpeg`
   - **Camera/Channel Name**: Display name (e.g., "Front Door Camera")
   - **Channel Number**: Unique channel number (e.g., 999)
3. Optional fields:
   - **Channel Group**: Organize cameras (default: "Security Cameras")
   - **Stream Logo URL**: URL to a logo/icon for the stream
4. Click "➕ Create Camera Channel"

### Updating a Camera Channel

1. Enter the **Channel Number** of the camera you want to update
2. Fill in any fields you want to change (leave blank to keep existing values)
3. Click "✏️ Update Camera Channel"

### Deleting a Camera Channel

1. Enter the **Channel Number** of the camera you want to delete
2. Click "🗑 Delete Camera Channel"
3. Confirm the deletion

### Listing All Camera Channels

- Click "📋 List All Camera Channels" to see all cameras in security-related groups
- Shows channel number, name, group, and stream URL for each camera

## Supported Stream Formats

### RTSP (Recommended)
Most IP cameras support RTSP. Common formats:
- `rtsp://ip:554/stream1`
- `rtsp://username:password@ip:554/stream1`
- `rtsp://ip:554/Streaming/Channels/101`

### HTTP/MJPEG
Some cameras provide HTTP streams:
- `http://ip:8080/video`
- `http://username:password@ip/mjpeg`

### Tips for Finding Your Camera's Stream URL
- Check your camera's manual or manufacturer website
- Common ports: 554 (RTSP), 8080 (HTTP), 80 (HTTP)
- Try tools like VLC Media Player to test URLs
- Search online: "[camera model] rtsp url"

## Troubleshooting

### Stream Not Playing

**Check FFmpeg warnings in logs:**
- `method SETUP failed: 461 Unsupported Transport` - Normal, FFmpeg will retry with different transport
- `Timestamps are unset` - Cosmetic warning, stream will work fine

**Common issues:**
- Wrong credentials in URL
- Camera requires specific RTSP transport (TCP vs UDP)
- Firewall blocking access to camera
- Camera stream path incorrect

### Channel Number Already Exists

Each channel must have a unique number. Use the "List" function to see existing channels and choose a different number.

### Logo Not Displaying

- Logo URLs are optional and only affect the stream display
- If logo fetch fails, the channel will still work fine
- Make sure the logo URL is publicly accessible

## Technical Details

### Model Structure
- Uses `dispatcharr_channels.Channel` for channel data
- Uses `dispatcharr_channels.Stream` for stream URLs
- Uses `dispatcharr_channels.ChannelStream` for channel-stream linking
- Uses `dispatcharr_channels.ChannelGroup` for organization

### Stream Processing
- Dispatcharr uses FFmpeg to process camera streams
- Streams are transcoded to MPEG-TS format for compatibility
- Supports HEVC (H.265), H.264, and other codecs
- Handles both video and audio streams

## Version

**Version:** 1.0.0  
**Author:** Community Plugin

## Support

For issues or questions:
1. Check Dispatcharr logs for detailed error messages
2. Verify your camera stream URL works in VLC or another player
3. Ensure camera is accessible from the Dispatcharr server

## License

Community plugin for Dispatcharr. Free to use and modify.
