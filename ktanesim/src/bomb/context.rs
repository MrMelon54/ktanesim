use crate::prelude::*;
use std::sync::Arc;

/// Helper function that, given a [`Context`] returns the [`Bomb`] for a given [`Message`]. If no
/// bomb is ticking in the message's channel, [`None`] is returned.
pub fn get_bomb(handler: &Handler, channel: ChannelId) -> Option<BombRef> {
    handler.bombs.read().get(&channel).map(Arc::clone)
}

/// Helper wrapper around [`get_bomb`] that returns an error message if there is no bomb.
pub fn need_bomb(handler: &Handler, channel: ChannelId) -> Result<BombRef, ErrorMessage> {
    get_bomb(handler, channel).ok_or(ErrorMessage::NoBomb)
}

/// Helper function that, given a [`Context`] returns whether a bomb is ticking in the channel
/// corresponding to a [`Message`].
pub fn running_in(handler: &Handler, channel: ChannelId) -> bool {
    handler.bombs.read().contains_key(&channel)
}

pub fn end_bomb(
    handler: &Handler,
    bomb: &mut BombData,
    drop_callback: impl FnOnce(&mut BombData) + Send + Sync + 'static,
) {
    // If .remove() returns None, the bomb is already going to end. The first callback is given
    // priority.
    if handler.bombs.write().remove(&bomb.channel).is_some() {
        bomb.timer.freeze();
        bomb.drop_callback = Some(Box::new(drop_callback));
        handler.schedule_presence_update();
    }
}

pub fn update_presence(handler: &Handler, ctx: &Context) {
    trace!("Updating Discord presence");
    let bomb_count = handler.bombs.read().len();
    let status = if bomb_count == 0 {
        OnlineStatus::Idle
    } else {
        OnlineStatus::Online
    };
    ctx.set_presence(
        Some(Activity::playing(&format!(
            "{} bomb{}. !help for help",
            bomb_count,
            if bomb_count == 1 { "" } else { "s" },
        ))),
        status,
    );
}
