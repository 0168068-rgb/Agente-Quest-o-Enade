export const failure=(message,code='PORTAL_ERROR')=>Object.assign(new Error(message),{code});
export const requiresUser=e=>['CANCELLED','MANUAL_CHANGES','SESSION_UNAVAILABLE','TAB_UNAVAILABLE','SAVE_IN_FLIGHT','ACCOUNT_CHANGED'].includes(e?.code);

// Retry reads, never a Save click. A persistent error belongs to its option;
// it is not a reason to abandon the rest of the account.
export async function attemptRead({client,read,onError=()=>{},cancelled=()=>false,attempts=2}){
  let error;
  for(let attempt=1;attempt<=attempts;attempt++){
    if(cancelled())throw failure('Consulta pausada pelo usuário.','CANCELLED');
    try{return {ok:true,value:await read(attempt)};}
    catch(e){
      if(requiresUser(e))throw e;
      error=e;onError(e,attempt);
      try{await client.recover();}catch(recovery){if(requiresUser(recovery))throw recovery;onError(recovery,attempt);}
    }
  }
  return {ok:false,error};
}
