"""
Security Camera Plugin for Dispatcharr
Add RTSP/HTTP/MJPEG security camera feeds as channels
"""

import logging

logger = logging.getLogger(__name__)


class Plugin:
    """Security Camera Channel Plugin"""
    
    name = "Security Camera"
    version = "1.0.0"
    description = "Add security camera feeds (RTSP/HTTP/MJPEG) as channels"
    author = "Community Plugin"
    
    # Settings fields
    fields = [
        {
            "id": "camera_url",
            "label": "Camera Stream URL",
            "type": "string",
            "required": True,
            "help": "RTSP, HTTP, or MJPEG stream URL (e.g., rtsp://user:pass@192.168.1.100:554/stream)"
        },
        {
            "id": "camera_name",
            "label": "Camera/Channel Name",
            "type": "string",
            "required": True,
            "default": "Security Camera",
            "help": "Display name for the camera channel"
        },
        {
            "id": "channel_number",
            "label": "Channel Number",
            "type": "number",
            "required": True,
            "default": 999,
            "help": "Channel number (e.g., 999)"
        },
        {
            "id": "channel_group",
            "label": "Channel Group",
            "type": "string",
            "required": False,
            "default": "Security Cameras",
            "help": "Group name to organize cameras"
        },
        {
            "id": "logo_url",
            "label": "Stream Logo URL (optional)",
            "type": "string",
            "required": False,
            "help": "URL to a logo/icon for the stream (displayed in stream listings)"
        }
    ]
    
    # Actions (buttons)
    actions = [
        {
            "id": "create_channel",
            "label": "➕ Create Camera Channel",
            "description": "Create a new channel for this camera",
            "confirm": True
        },
        {
            "id": "update_channel",
            "label": "✏️ Update Camera Channel",
            "description": "Update existing camera channel settings"
        },
        {
            "id": "delete_channel",
            "label": "🗑 Delete Camera Channel",
            "description": "Remove this camera channel",
            "confirm": True
        },
        {
            "id": "list_cameras",
            "label": "📋 List All Camera Channels",
            "description": "Show all camera channels"
        }
    ]
    
    def run(self, action, params, context):
        """Execute plugin actions"""
        logger_ctx = context.get("logger")
        settings = context.get("settings", {})
        
        logger_ctx.info(f"Security Camera Plugin: Running action '{action}'")
        
        try:
            if action == "create_channel":
                return self._create_channel(settings, logger_ctx)
            elif action == "update_channel":
                return self._update_channel(settings, logger_ctx)
            elif action == "delete_channel":
                return self._delete_channel(settings, logger_ctx)
            elif action == "list_cameras":
                return self._list_cameras(logger_ctx)
            else:
                return {"success": False, "message": f"Unknown action: {action}"}
                
        except Exception as e:
            logger_ctx.error(f"Error in Security Camera Plugin: {e}", exc_info=True)
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def _create_channel(self, settings, logger_ctx):
        """Create a new camera channel"""
        from django.apps import apps
        
        Channel = apps.get_model('dispatcharr_channels', 'Channel')
        Stream = apps.get_model('dispatcharr_channels', 'Stream')
        ChannelStream = apps.get_model('dispatcharr_channels', 'ChannelStream')
        ChannelGroup = apps.get_model('dispatcharr_channels', 'ChannelGroup')
        
        camera_url = settings.get("camera_url", "").strip()
        camera_name = settings.get("camera_name", "Security Camera").strip()
        channel_number = int(settings.get("channel_number", 999))
        channel_group_name = settings.get("channel_group", "Security Cameras").strip()
        logo_url = settings.get("logo_url", "").strip()
        
        if not camera_url:
            return {"success": False, "message": "❌ Camera URL is required"}
        
        if not camera_name:
            return {"success": False, "message": "❌ Camera name is required"}
        
        # Check if channel number already exists
        existing_channel = Channel.objects.filter(channel_number=channel_number).first()
        if existing_channel:
            return {
                "success": False,
                "message": f"❌ Channel #{channel_number} already exists: '{existing_channel.name}'\nChoose a different number."
            }
        
        try:
            # Get or create the channel group
            channel_group, created = ChannelGroup.objects.get_or_create(
                name=channel_group_name
            )
            if created:
                logger_ctx.info(f"Created new channel group: {channel_group_name}")
            
            # Create the stream
            stream = Stream.objects.create(
                name=f"{camera_name} Stream",
                url=camera_url,
                logo_url=logo_url if logo_url else ""
            )
            logger_ctx.info(f"Created stream: {stream.name}")
            
            # Create the channel (logo is optional and requires a Logo model instance)
            channel = Channel.objects.create(
                name=camera_name,
                channel_number=channel_number
            )
            logger_ctx.info(f"Created channel: {channel.name} (#{channel_number})")
            
            # Associate stream with channel using ChannelStream
            channel_stream = ChannelStream.objects.create(
                channel=channel,
                stream=stream,
                order=0
            )
            logger_ctx.info(f"Linked channel and stream")
            
            # Add channel to group
            channel_group.channels.add(channel)
            logger_ctx.info(f"Added channel to group: {channel_group_name}")
            
            return {
                "success": True,
                "message": f"✅ Camera channel '{camera_name}' created successfully!\n\n"
                          f"📺 Channel Number: {channel_number}\n"
                          f"📁 Group: {channel_group_name}\n"
                          f"🔗 Stream URL: {camera_url[:50]}{'...' if len(camera_url) > 50 else ''}\n\n"
                          f"Go to Channels page to view your new camera!"
            }
            
        except Exception as e:
            logger_ctx.error(f"Failed to create channel: {e}", exc_info=True)
            return {"success": False, "message": f"❌ Failed to create channel: {str(e)}"}
    
    def _update_channel(self, settings, logger_ctx):
        """Update an existing camera channel"""
        from django.apps import apps
        
        Channel = apps.get_model('dispatcharr_channels', 'Channel')
        Stream = apps.get_model('dispatcharr_channels', 'Stream')
        ChannelStream = apps.get_model('dispatcharr_channels', 'ChannelStream')
        ChannelGroup = apps.get_model('dispatcharr_channels', 'ChannelGroup')
        
        channel_number = int(settings.get("channel_number", 999))
        
        channel = Channel.objects.filter(channel_number=channel_number).first()
        
        if not channel:
            return {
                "success": False,
                "message": f"❌ Channel #{channel_number} not found\nUse 'Create Camera Channel' first."
            }
        
        try:
            camera_name = settings.get("camera_name", "").strip()
            if camera_name:
                channel.name = camera_name
            
            channel.save()
            logger_ctx.info(f"Updated channel: {channel.name}")
            
            # Update channel group if provided
            channel_group_name = settings.get("channel_group", "").strip()
            if channel_group_name:
                # Remove from old groups
                old_groups = ChannelGroup.objects.filter(channels=channel)
                for old_group in old_groups:
                    old_group.channels.remove(channel)
                
                # Add to new group
                channel_group, created = ChannelGroup.objects.get_or_create(
                    name=channel_group_name
                )
                channel_group.channels.add(channel)
                logger_ctx.info(f"Moved channel to group: {channel_group_name}")
            
            # Update stream URL if provided
            camera_url = settings.get("camera_url", "").strip()
            logo_url = settings.get("logo_url", "").strip()
            
            if camera_url:
                channel_stream = ChannelStream.objects.filter(channel=channel).first()
                if channel_stream:
                    stream = channel_stream.stream
                    stream.url = camera_url
                    if logo_url:
                        stream.logo_url = logo_url
                    stream.save()
                    logger_ctx.info(f"Updated stream URL")
                else:
                    # Create new stream if none exists
                    stream = Stream.objects.create(
                        name=f"{camera_name if camera_name else channel.name} Stream",
                        url=camera_url,
                        logo_url=logo_url if logo_url else ""
                    )
                    ChannelStream.objects.create(
                        channel=channel,
                        stream=stream,
                        order=0
                    )
                    logger_ctx.info(f"Created new stream for channel")
            
            # Get current group for display
            current_groups = ChannelGroup.objects.filter(channels=channel)
            group_display = ", ".join([g.name for g in current_groups]) if current_groups.exists() else "None"
            
            return {
                "success": True,
                "message": f"✅ Camera channel #{channel_number} updated successfully!\n\n"
                          f"📺 Name: {channel.name}\n"
                          f"📁 Group: {group_display}"
            }
            
        except Exception as e:
            logger_ctx.error(f"Failed to update channel: {e}", exc_info=True)
            return {"success": False, "message": f"❌ Failed to update channel: {str(e)}"}
    
    def _delete_channel(self, settings, logger_ctx):
        """Delete a camera channel"""
        from django.apps import apps
        
        Channel = apps.get_model('dispatcharr_channels', 'Channel')
        ChannelStream = apps.get_model('dispatcharr_channels', 'ChannelStream')
        
        channel_number = int(settings.get("channel_number", 999))
        
        channel = Channel.objects.filter(channel_number=channel_number).first()
        
        if not channel:
            return {
                "success": False,
                "message": f"❌ Channel #{channel_number} not found"
            }
        
        try:
            channel_name = channel.name
            
            # Delete associated streams through ChannelStream
            channel_streams = ChannelStream.objects.filter(channel=channel)
            for cs in channel_streams:
                stream = cs.stream
                cs.delete()
                # Only delete the stream if no other channels use it
                if not ChannelStream.objects.filter(stream=stream).exists():
                    stream.delete()
                    logger_ctx.info(f"Deleted stream: {stream.name}")
            
            # Delete the channel
            channel.delete()
            logger_ctx.info(f"Deleted channel: {channel_name} (#{channel_number})")
            
            return {
                "success": True,
                "message": f"✅ Camera channel '{channel_name}' (#{channel_number}) deleted successfully!"
            }
            
        except Exception as e:
            logger_ctx.error(f"Failed to delete channel: {e}", exc_info=True)
            return {"success": False, "message": f"❌ Failed to delete channel: {str(e)}"}
    
    def _list_cameras(self, logger_ctx):
        """List all camera channels"""
        from django.apps import apps
        
        Channel = apps.get_model('dispatcharr_channels', 'Channel')
        ChannelStream = apps.get_model('dispatcharr_channels', 'ChannelStream')
        ChannelGroup = apps.get_model('dispatcharr_channels', 'ChannelGroup')
        
        try:
            # Find channels in security camera groups
            security_groups = ChannelGroup.objects.filter(name__icontains="Security")
            cameras = []
            
            for group in security_groups:
                cameras.extend(group.channels.all())
            
            # Remove duplicates and sort
            cameras = list(set(cameras))
            cameras.sort(key=lambda x: x.channel_number)
            
            if not cameras:
                return {
                    "success": True,
                    "message": "📹 No security camera channels found\n\nCreate one using 'Create Camera Channel'!"
                }
            
            camera_list = []
            for cam in cameras:
                # Get stream info
                channel_stream = ChannelStream.objects.filter(channel=cam).first()
                stream_url = ""
                if channel_stream:
                    stream_url = channel_stream.stream.url
                    stream_url = stream_url[:50] + "..." if len(stream_url) > 50 else stream_url
                
                # Get group info - query groups that contain this channel
                groups = ChannelGroup.objects.filter(channels=cam)
                group_names = ", ".join([g.name for g in groups]) if groups.exists() else "None"
                
                camera_list.append(
                    f"📺 #{cam.channel_number}: {cam.name}\n"
                    f"   📁 {group_names}\n"
                    f"   🔗 {stream_url if stream_url else 'No stream'}"
                )
            
            message = f"📹 Security Camera Channels ({len(cameras)} found):\n\n" + "\n\n".join(camera_list)
            
            return {"success": True, "message": message}
            
        except Exception as e:
            logger_ctx.error(f"Failed to list cameras: {e}", exc_info=True)
            return {"success": False, "message": f"❌ Failed to list cameras: {str(e)}"}
