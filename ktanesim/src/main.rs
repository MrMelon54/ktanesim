#![feature(
    proc_macro_hygiene,
    fnbox,
    futures_api, async_await, await_macro, try_blocks,
    type_ascription,
    try_trait,
)]

mod backoff;
mod bomb;
mod gateway;
mod modules;
mod prelude;
#[macro_use]
mod util_macros;

#[macro_use]
extern crate log;

use backoff::Backoff;
use gateway::event_loop;
use modules::wires;
use prelude::*;
use serenity::gateway::Shard;
use serenity::model::event::{Event, GatewayEvent};
use serenity::prelude::*;
use std::io::prelude::*;
use tokio::prelude::*;
use tokio_async_await::compat::forward::IntoAwaitable;

fn main() {
    tokio::run_async(
        async {
            if let Err(err) = kankyo::load() {
                eprintln!("Couldn't load .env file: {:?}", err);
            }

            env_logger::init();
            let token = kankyo::key("DISCORD_TOKEN").expect("Token not present in environment");
            let mut shard = awaitt!(Shard::new(token, [0, 1])).expect("Couldn't create shard");
            let mut messages = shard.messages().unwrap();
            let mut backoff = Backoff::new();

            loop {
                let event: Result<Option<Event>, Error> = try {
                    let message = await!(messages.next())??;
                    let event = shard.parse(&message)?;
                    use serenity::gateway::Action;
                    if let Some(action) = shard.process(&event)? {
                        match action {
                            Action::Identify => {
                                trace!("Identifying");
                                shard.identify()?;
                                continue;
                            }
                            Action::Autoreconnect => {
                                trace!("Shard requested autoreconnect");
                                awaitt!(backoff.delay())?;
                                awaitt!(shard.autoreconnect())?;
                                messages = shard.messages().unwrap();
                            }
                            Action::Reconnect => {
                                trace!("Shard requested reconnect");
                                awaitt!(backoff.delay())?;
                                awaitt!(shard.reconnect())?;
                                messages = shard.messages().unwrap();
                                continue;
                            }
                            Action::Resume => {
                                trace!("Resuming");
                                awaitt!(shard.resume())?;
                                messages = shard.messages().unwrap();
                                continue;
                            }
                        }
                    }

                    if let GatewayEvent::Dispatch(_, event) = event {
                        Some(event)
                    } else {
                        None
                    }
                };

                if let Ok(event) = event {
                    if let Some(event) = event {
                        backoff.success();
                    }
                } else {
                    warn!("Event loop error, reconnecting: {:?}", event.unwrap_err());
                    while let Err(why) = awaitt!(backoff
                        .delay()
                        .from_err()
                        .and_then(|()| shard.autoreconnect().from_err())):
                        Result<_, Error>
                    {
                        backoff.failure();
                        warn!("Error while reconnecting: {:?}", why);
                    }

                    messages = shard.messages().unwrap();
                }
            }
        },
    );
}

// Box<dyn Error> is not Send or Sync, so we need to do this...
use tokio::timer::Error as TimerError;
use tungstenite::error::Error as TungsteniteError;

#[derive(Debug)]
enum Error {
    None,
    Tungstenite(TungsteniteError),
    Serenity(SerenityError),
    Timer(TimerError),
}

impl From<std::option::NoneError> for Error {
    fn from(_: std::option::NoneError) -> Error {
        Error::None
    }
}

impl From<TungsteniteError> for Error {
    fn from(err: TungsteniteError) -> Error {
        Error::Tungstenite(err)
    }
}

impl From<SerenityError> for Error {
    fn from(err: SerenityError) -> Error {
        Error::Serenity(err)
    }
}

impl From<TimerError> for Error {
    fn from(err: TimerError) -> Error {
        Error::Timer(err)
    }
}
