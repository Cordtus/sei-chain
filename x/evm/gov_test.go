package evm_test

import (
	"testing"

	testkeeper "github.com/sei-protocol/sei-chain/testutil/keeper"
	"github.com/sei-protocol/sei-chain/x/evm"
	"github.com/sei-protocol/sei-chain/x/evm/types"
	"github.com/stretchr/testify/require"
)

func TestAddERCNativePointerProposals(t *testing.T) {
	k, ctx := testkeeper.MockEVMKeeper()
	_, pointer1 := testkeeper.MockAddressPair()
	_, pointer2 := testkeeper.MockAddressPair()
	require.Nil(t, evm.HandleAddERCNativePointerProposal(ctx, k, &types.AddERCNativePointerProposal{
		Token:   "test",
		Version: 1,
		Pointer: pointer1.Hex(),
	}))
	addr, ver, exists := k.GetERC20NativePointer(ctx, "test")
	require.True(t, exists)
	require.Equal(t, uint16(1), ver)
	require.Equal(t, addr, pointer1)
	require.Nil(t, evm.HandleAddERCNativePointerProposal(ctx, k, &types.AddERCNativePointerProposal{
		Token:   "test",
		Version: 2,
		Pointer: pointer2.Hex(),
	}))
	addr, ver, exists = k.GetERC20NativePointer(ctx, "test")
	require.True(t, exists)
	require.Equal(t, uint16(2), ver)
	require.Equal(t, addr, pointer2)
	require.Nil(t, evm.HandleAddERCNativePointerProposal(ctx, k, &types.AddERCNativePointerProposal{
		Token:   "test",
		Version: 2,
	}))
	addr, ver, exists = k.GetERC20NativePointer(ctx, "test")
	require.True(t, exists)
	require.Equal(t, uint16(1), ver)
	require.Equal(t, addr, pointer1)
}

func TestAddERCCW20PointerProposals(t *testing.T) {
	k, ctx := testkeeper.MockEVMKeeper()
	_, pointer1 := testkeeper.MockAddressPair()
	_, pointer2 := testkeeper.MockAddressPair()
	require.Nil(t, evm.HandleAddERCCW20PointerProposal(ctx, k, &types.AddERCCW20PointerProposal{
		Pointee: "test",
		Version: 1,
		Pointer: pointer1.Hex(),
	}))
	addr, ver, exists := k.GetERC20CW20Pointer(ctx, "test")
	require.True(t, exists)
	require.Equal(t, uint16(1), ver)
	require.Equal(t, addr, pointer1)
	require.Nil(t, evm.HandleAddERCCW20PointerProposal(ctx, k, &types.AddERCCW20PointerProposal{
		Pointee: "test",
		Version: 2,
		Pointer: pointer2.Hex(),
	}))
	addr, ver, exists = k.GetERC20CW20Pointer(ctx, "test")
	require.True(t, exists)
	require.Equal(t, uint16(2), ver)
	require.Equal(t, addr, pointer2)
	require.Nil(t, evm.HandleAddERCCW20PointerProposal(ctx, k, &types.AddERCCW20PointerProposal{
		Pointee: "test",
		Version: 2,
	}))
	addr, ver, exists = k.GetERC20CW20Pointer(ctx, "test")
	require.True(t, exists)
	require.Equal(t, uint16(1), ver)
	require.Equal(t, addr, pointer1)
}

func TestAddERCCW721PointerProposals(t *testing.T) {
	k, ctx := testkeeper.MockEVMKeeper()
	_, pointer1 := testkeeper.MockAddressPair()
	_, pointer2 := testkeeper.MockAddressPair()
	require.Nil(t, evm.HandleAddERCCW721PointerProposal(ctx, k, &types.AddERCCW721PointerProposal{
		Pointee: "test",
		Version: 1,
		Pointer: pointer1.Hex(),
	}))
	addr, ver, exists := k.GetERC721CW721Pointer(ctx, "test")
	require.True(t, exists)
	require.Equal(t, uint16(1), ver)
	require.Equal(t, addr, pointer1)
	require.Nil(t, evm.HandleAddERCCW721PointerProposal(ctx, k, &types.AddERCCW721PointerProposal{
		Pointee: "test",
		Version: 2,
		Pointer: pointer2.Hex(),
	}))
	addr, ver, exists = k.GetERC721CW721Pointer(ctx, "test")
	require.True(t, exists)
	require.Equal(t, uint16(2), ver)
	require.Equal(t, addr, pointer2)
	require.Nil(t, evm.HandleAddERCCW721PointerProposal(ctx, k, &types.AddERCCW721PointerProposal{
		Pointee: "test",
		Version: 2,
	}))
	addr, ver, exists = k.GetERC721CW721Pointer(ctx, "test")
	require.True(t, exists)
	require.Equal(t, uint16(1), ver)
	require.Equal(t, addr, pointer1)
}
